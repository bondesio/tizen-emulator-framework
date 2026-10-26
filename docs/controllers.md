# Gamepad option and implementation contract

This contract comes from the local TizNES implementation and its root watcher,
not from a proposed input API. Use its C functions and data flow as the porting
reference; keep the core's own button bitfield and additional system buttons.

## Settings presented to the user

Keep these selectable rows together, in this order:

| Row | Required behavior |
| --- | --- |
| Player 1 controller | List readable, button-capable physical USB pads with a name and identity; first startup can auto-select the first real pad. TizNES uses Virtual Gamepad only as a last shared fallback. |
| Player 2 controller | Separate picker, initially **None (single player)**. One physical device cannot occupy both slots. Selecting the other slot's device swaps assignments, releasing its old grab first. |
| Exclusive capture: On / Off | Persisted global preference; **On by default**. Reopen/re-evaluate both selected slots immediately after changing it. Off releases grabs and uses shared input. |
| Map player 1 controls | Guided, release-then-press mapping of each emulated action for the selected model. Report that a controller must be connected before starting. |
| Map player 2 controls | Same flow for P2. The mapping belongs to the controller model, not the player number. |
| Guided gamepad input diagnostic | At minimum the TizNES P1 flow: prompts for individual controls, logs raw type/code/value, source (`evdev`/`joydev`), reported joydev index and interpreted action; supports remote OK to skip and Back to cancel. Diagnostics must not remap controls. |

The diagnostic is a product feature for investigating physical controllers; it
does not require running a local automated test harness. Do not infer a working
grab from the preference or from successful `open(jsN)`.

The guided mapper must distinguish “capture is active” from “the last capture
timed out” and “no controller is connected.” Keep the named action visible,
provide a retry for that action, and make skip/cancel behavior explicit. Only
advance after an accepted event for the requested action; a timer or unrelated
button must not count as success. If the app pauses for a TV overlay, cancel
and re-arm the current action on resume. Recheck current capture state when
routing remote keys, since a timeout or accepted event can arrive between UI
animation ticks.

## Preference, runtime state and fallback

Keep `exclusive_preferred` separate from each pad's `capture_exclusive`, open
descriptors, selected physical identity, mapping and capture error string.

| Preference / actual state | Honest UI |
| --- | --- |
| On, successful `EVIOCGRAB` | `Controller name [exclusive]`; `Exclusive capture active` |
| On, selected device readable only through joydev | `Controller name [shared]`; `Exclusive capture: On (waiting for device access)`; disclose that Tizen shortcuts may fire |
| Off, connected | `Controller name [shared]`; `Exclusive capture: Off; controller buttons may reach Tizen` |
| Selected device absent | `Not connected`; retain its saved identity for reconnect |
| No P2 assignment | `None (single player)` |

Log the matching event number, open/grab errno, and read/write access results
when capture fails. Rate-limit repeated diagnostics. Continue shared joydev
input when available and periodically retry capture while preferred On (TizNES
uses roughly half-second app retries; the watcher polls once per second).
Show the **actual** state in every capture hint, including the toggle row;
never announce shortcut suppression for a failed grab or for an absent P2 pad.

## Device identity and grabbing

1. Identify a pad as `vid:pid:serial:usb-port` by walking from its sysfs input
   device to the USB ancestor. Names and `jsN`/`eventN` numbers are display or
   transient enumeration data, not stable identities.
2. Reject joystick nodes whose `capabilities/key` has no nonzero bits. A DS4
   exposes a buttonless motion-sensor joystick under the same USB identity as
   its actual controller; choosing it breaks mapping and grab resolution.
3. Prefer the full saved identity. If a nonempty serial is present, allow a
   different USB port only when exactly one button-capable pad matches that
   vendor/product/serial. Pads without serials stay bound to their USB port.
   Re-resolve after disconnect and before retries; do not fall through to an
   unrelated connected pad when a saved device is missing.
   First-run Auto selection must be able to discover a readable joydev pad
   before its event node has been granted. Resolve P1 and P2 to distinct
   physical devices; do not deduplicate two `auto` preferences before resolving
   them, or the second slot can never receive its first grant.
4. Compare the selected `jsN/device` and candidate `eventN/device` sysfs parents.
   Open only its matching event node with `O_RDONLY | O_NONBLOCK` and request
   `EVIOCGRAB`. Never probe-grab all event nodes or choose one by device name.
   The root watcher requires exactly one joystick parent and event-node match;
   fail closed if resolution is ambiguous.
5. Successful grab means raw evdev becomes the input source. Avoid consuming
   both raw and joydev events as separate actions. Translate joydev button and
   axis indices through `JSIOCGBTNMAP` / `JSIOCGAXMAP`; evdev uses Linux key/ABS
   codes directly. Query `EVIOCGABS` ranges for deadzones and normalize axes;
   do not compare evdev ABS codes to packed joydev axis indices.
   The joydev map ioctls can fail on otherwise readable controllers. Treat the
   button/axis counts and maps as separate queries: keep the pad when counts
   succeed, then use bounded standard button/hat fallbacks and the raw evdev
   mapper when available. Unknown axes must use an invalid sentinel rather than
   aliasing X/Y; an unknown map must not make every button unreachable.
6. Handle `SYN_DROPPED` by discarding until the next `SYN_REPORT`, then resync
   key/axis state. Clear all held action bits on detach/state transitions.
7. Release `EVIOCGRAB` and close both descriptors when replacing/detaching a
   controller and on app exit. Prevent exit-time polling from reopening them.
   Define focus-loss/pause behavior deliberately in the consumer; do not
   assume an app shutdown hook covers every Tizen lifecycle transition.

Only shared joydev events should activate the short duplicate-navigation-key
suppression window used for Tizen's synthesized keys. An exclusively grabbed
pad's analog jitter must never swallow real TV-remote keys. TizNES lets either
assigned controller navigate menus, combining their action bits and neutralizing
opposing directions. Keep per-slot input separate for gameplay and mapping;
the guided raw-input diagnostic explicitly targets P1.

## Persistence and mappings

TizNES writes a small watcher-facing file, parsed as data, never sourced:

```ini
exclusive=1
identity=054c:09cc::1-1
identity2=0e6f:0213:EXAMPLE-SERIAL:1-2
```

The values above illustrate the format; they are not default assignments. A new
app starts with `exclusive=1` and empty/unassigned identities. Give the file its
own app-data path. Save physical assignments here, and save mappings separately
per **vendor/product model**, e.g. `<app>-map-054c-09cc.bin`. Mapping the same model
for P2 affects that model's mapping for P1 too; say so in the footer. Preserve
defaults only for actions without a user mapping so a stick click cannot retain
an unwanted default Start/Select action after remapping. Include native controls
such as Neo Geo A/B/C/D or GBA L/R in the mapping sequence.

TizNES's legacy binary settings layout is compatibility scaffolding, not a new
file-format requirement. A new app may use bounded key/value settings and its
own versioned model-map format; do not import another system's action bitmask.

## Root watcher boundaries

Start from [TizNES's `input-watcher/watch.sh`](https://github.com/bondesio/tiznes/blob/main/input-watcher/watch.sh); compare [TizGB's
`input-watcher/watch.sh`](https://github.com/bondesio/tizgb/blob/main/input-watcher/watch.sh) for the app-specific module layout.
Use unique config, state, log, unit and boot-module names for every emulator.
The watcher grants access; **the app's `EVIOCGRAB` establishes capture**.

- Only handle the selected button-capable USB controller's unique matching
  input character device (major 13); never change a remote/keyboard node.
- Validate identities and node paths; parse known key/value lines only.
  Use bounded sysfs traversal. Never execute content from app-owned config.
- On this TV a grant is `owner:users 0600`; stock restore is `root:input 0660`.
  Restore only a recorded node that still carries the watcher's grant.
- Adopt recorded stale grants after watcher restart, re-resolve after replug,
  and perform release before grant when moving/swapping selections.
- Signal handlers must restore **and exit**. Merely restoring in SIGTERM lets
  the loop resume and re-grant before a later SIGKILL.
- All three current watchers serialize permission changes and state-file
  updates with `/usr/bin/flock` on `/run/tizen-input-access.lock`. Keep the lock
  across foreign-state checks, release/grant operations and state publication;
  never check first and lock later.
- Publish the selected event path atomically **before** changing ownership or
  mode. Signal cleanup can then find a partially granted node. Restore only
  when the recorded node is still owned by this watcher or carries a partial
  stock restore; never infer ownership from `owner:users` alone.
- New emulators must read existing watcher records while holding the shared
  lock and yield to a recorded owner. TizNES is the current priority owner; a
  future priority change must update every cooperating watcher together.
- If the target lacks `/usr/bin/flock`, fail closed and report capture as
  unavailable. Do not silently fall back to racing ownership changes.

This kit documents the shared protocol but installs no root module itself.

## Local source map

Read [`app/nes_main.c` in TizNES](https://github.com/bondesio/tiznes/blob/main/app/nes_main.c) around these named functions:

| Concern | Existing C implementation |
| --- | --- |
| Per-slot state | `pad_t`, `pads_init`, `pad_forget_device` |
| Identity and enumeration | `js_has_buttons`, `usb_identity_for_js`, `pad_resolve_index`, `scan_js_devices` |
| Capture and fallback | `js_open_device`, `js_close_device`, `pad_poll`, `ev_resync` |
| Two-player assignment | `device_select_activate`, `pad_reopen` |
| Per-model persistence | `identity_model`, `pad_apply_mapping`, `pad_save_model_mapping` |
| Mapping and diagnostics | `mapping_start`, `mapping_advance`, `input_test_start`, `input_test_event` |
| UI and duplicate keys | `pad_status_text`, `render_settings`, `on_key_down`, `joystick_key_was_recent` |

These paths are porting references, not a linkable ABI. TizGB uses one gameplay
controller; its watcher retaining a second identity key does not make its UI a
two-player implementation. TizNES is the two-slot reference.

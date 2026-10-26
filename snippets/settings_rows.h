/* Copy into an emulator's frontend and remove unsupported options.
 * No Evas dependency or runtime API; headers are separate from row IDs.
 * The complete two-player list requires a scrolling viewport on 1080p.
 */
#ifndef EMULATOR_STARTER_SETTINGS_ROWS_H
#define EMULATOR_STARTER_SETTINGS_ROWS_H

enum {
    S_P1_DEVICE, S_P2_DEVICE, S_EXCLUSIVE, S_MAP_P1, S_MAP_P2, S_INPUT_DIAG,
    S_VOLUME, S_MUTE,
    S_SCALE, S_FILTER, S_SCANLINES,
    S_CORE_MODE, S_REGION, S_PERF_OVERLAY, S_RESCAN, S_BACK, S_EXIT,
    SETTINGS_ROWS
};

typedef struct {
    int first_row;
    const char *title;
} settings_section;

static const settings_section g_settings_sections[] = {
    { S_P1_DEVICE, "CONTROLLERS" },
    { S_VOLUME,    "AUDIO" },
    { S_SCALE,     "VIDEO" },
    { S_CORE_MODE, "SYSTEM" }
};

#define SETTINGS_SECTIONS \
    ((int)(sizeof g_settings_sections / sizeof g_settings_sections[0]))

/* Up:   if (g_settings_sel > 0) --g_settings_sel;
 * Down: if (g_settings_sel < SETTINGS_ROWS - 1) ++g_settings_sel;
 * Draw titles before their first_row; never put them in this selection range.
 * Both highlight text and cursor placement use g_settings_sel, not g_sel.
 */

#endif

/* Copy into an emulator's frontend. Library row layout shared by all emulators:
 *
 *   row 0                  Exit <App>                (always present)
 *   rows 1 .. game_count   games, in sorted order
 *   row game_count + 1     Settings and controller setup  (always present)
 *
 * Both fixed rows exist even with zero games. Reference: TizGBA gba_main.c.
 * Game index = row - 1. Selection is bounded to [0, LIBRARY_ROWS(n) - 1].
 */
#ifndef EMULATOR_STARTER_LIBRARY_ROWS_H
#define EMULATOR_STARTER_LIBRARY_ROWS_H

#define LIBRARY_ROW_EXIT 0
#define LIBRARY_ROWS(game_count)         ((game_count) + 2)
#define LIBRARY_ROW_SETTINGS(game_count) ((game_count) + 1)
#define LIBRARY_ROW_IS_GAME(row, game_count) \
    ((row) >= 1 && (row) <= (game_count))

/* Activation (remote OK / gamepad A), after clearing held input bits:
 *   if (row == LIBRARY_ROW_EXIT)                    app_exit();
 *   else if (scanning)                              ;  // ignore until scan ends
 *   else if (row == LIBRARY_ROW_SETTINGS(n))        settings_open();
 *   else                                            start_game(row - 1);
 *
 * After a rescan, re-find the previously selected game by path/hash and set
 * row = index + 1; otherwise clamp to LIBRARY_ROW_SETTINGS(n).
 */

#endif

/* Host test for snippets/perf_overlay.h: cc -Wall -Wextra -I snippets tests/test_perf_overlay.c */
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "perf_overlay.h"

int main(void)
{
    perf_stats p;
    char buf[160];
    unsigned long long now = 5000000000ULL, period = 16666667ULL;  /* 60 Hz */
    int published = 0;

    perf_reset(&p, now);
    assert(perf_format(&p, PERF_OVERLAY_FPS, 6000, 0, buf, sizeof buf) == 0 && buf[0] == '\0');

    for (int i = 0; i < 59; i++) {
        now += period;
        published += perf_frame(&p, now, 2000000, 0);
    }
    assert(published == 0);                          /* window not full yet */
    now += period;
    assert(perf_frame(&p, now, 14000000, 1) == 1);   /* 60th frame closes the window */
    assert(p.fps_x100 >= 5990 && p.fps_x100 <= 6010);
    assert(p.late_frames == 1 && p.work_max_us == 14000);

    assert(perf_format(&p, PERF_OVERLAY_OFF, 6000, 0, buf, sizeof buf) == 0);
    assert(perf_format(&p, PERF_OVERLAY_FPS, 6000, 0, buf, sizeof buf) > 0);
    assert(strcmp(buf, "60.0 FPS") == 0);
    assert(perf_format(&p, PERF_OVERLAY_DETAILED, 6000, 3, buf, sizeof buf) > 0);
    assert(strstr(buf, "late 1") && strstr(buf, "audio under 3") && strstr(buf, "/ 60.00 FPS"));

    /* Counters restart for the next window; published values persist. */
    assert(p.frames == 0 && p.late == 0 && p.valid == 1);

    /* Clock going backwards must not publish or divide by zero. */
    perf_reset(&p, now);
    assert(perf_frame(&p, now - 1, 1000, 0) == 0);

    assert(perf_mode_sanitize(-1) == PERF_OVERLAY_OFF && perf_mode_sanitize(99) == PERF_OVERLAY_OFF);
    assert(perf_mode_next(PERF_OVERLAY_DETAILED) == PERF_OVERLAY_OFF);
    assert(strcmp(perf_mode_label(PERF_OVERLAY_DETAILED), "Detailed") == 0);

    /* Tiny buffer is truncated safely. */
    p.valid = 1; p.fps_x100 = 5994;
    char tiny[4];
    perf_format(&p, PERF_OVERLAY_FPS, 6000, 0, tiny, sizeof tiny);
    assert(strlen(tiny) == 3);
    return 0;
}

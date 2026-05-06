def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    sd_best, tx_best, ty_best = None, None, None
    sd_denom, tx_denom, ty_denom = -10**9, None, None

    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)

        # Baseline: aim for resources where we can beat opponent soon.
        val_us = (od - sd) * 22 - sd - (rx + ry) * 0.001
        if sd_best is None or val_us > sd_best:
            sd_best, tx_best, ty_best = val_us, rx, ry

        # Denial: only consider resources where opponent is closer.
        if od + 1 < sd:
            val_den = (sd - od) * 28 - sd - od - (rx + ry) * 0.001
            if val_den > sd_denom:
                sd_denom, tx_denom, ty_denom = val_den, rx, ry

    # Switch to denial mode if it’s decisively better.
    if tx_denom is not None and sd_denom > 8 and (sd_best is None or sd_denom >= sd_best - 2):
        tx, ty = tx_denom, ty_denom
    else:
        tx, ty = tx_best, ty_best

    best_move = (0, 0)
    best_score = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                d_to = man(nx, ny, tx, ty)
                d_opp = man(nx, ny, ox, oy)
                opp_to = man(ox, oy, tx, ty)
                # Primary: reduce distance to target. Secondary: slightly move away from opponent to prevent escorting.
                sc = d_to * 10 - d_opp * 0.2 + (0 if opp_to == 0 else 0)
                if best_score is None or sc < best_score:
                    best_score = sc
                    best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
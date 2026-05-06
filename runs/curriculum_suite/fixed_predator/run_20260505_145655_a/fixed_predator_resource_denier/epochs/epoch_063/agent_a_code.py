def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

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

    # Target: maximize how much nearer we are than opponent (deny potential), prefer closer when tied.
    best = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        deny = od - sd
        t = (deny, -od, -sd, -rx * 0.0001 - ry * 0.0001, rx, ry)
        if best is None or t > best:
            best = t
    tx, ty = best[4], best[5]

    cx0, cy0 = (w - 1) / 2.0, (h - 1) / 2.0

    best_move = [0, 0]
    best_val = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue

            sd2 = man(nx, ny, tx, ty)
            od2 = man(ox, oy, tx, ty)

            # Also consider second-best resource lightly to avoid deadlocks.
            sec_pen = 0
            for rx, ry in resources:
                if (rx, ry) == (tx, ty):
                    continue
                alt_sd = man(nx, ny, rx, ry)
                alt_od = man(ox, oy, rx, ry)
                # If we'd be able to deny much better at an alternative, slightly favor it.
                v = (alt_od - alt_sd)
                if v > 1:
                    sec_pen = min(sec_pen, -v) if sec_pen else -v
                    break

            center_bias = -(((nx - cx0) ** 2 + (ny - cy0) ** 2) * 1e-4)
            val = (-sd2 * 3.0 + od2 * 1.0 + center_bias + (sec_pen if sec_pen else 0.0), -sd2, -abs(dx) - abs(dy))
            if best_val is None or val > best_val:
                best_val = val
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]
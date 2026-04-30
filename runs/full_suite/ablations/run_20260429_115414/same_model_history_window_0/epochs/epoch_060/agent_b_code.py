def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    grid_w, grid_h = observation["grid_width"], observation["grid_height"]
    gxmax, gymax = grid_w - 1, grid_h - 1

    if not resources:
        tx, ty = ox, oy
    else:
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = (rx - sx) * (rx - sx) + (ry - sy) * (ry - sy)
            od = (rx - ox) * (rx - ox) + (ry - oy) * (ry - oy)
            score = (od - sd, -sd)  # want largest advantage, then smallest self distance
            if best is None or score > best[0]:
                best = (score, (rx, ry))
        tx, ty = best[1] if best is not None else (sx, sy)

    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = clamp(sx + dx, 0, gxmax), clamp(sy + dy, 0, gymax)
        if (nx, ny) in obstacles:
            continue
        d2 = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)
        # Prefer moves that reduce distance to target; lightly discourage if opponent is much closer
        od2 = (tx - ox) * (tx - ox) + (ty - oy) * (ty - oy)
        adv = od2 - d2
        val = (d2, -adv, abs(dx) + abs(dy))
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
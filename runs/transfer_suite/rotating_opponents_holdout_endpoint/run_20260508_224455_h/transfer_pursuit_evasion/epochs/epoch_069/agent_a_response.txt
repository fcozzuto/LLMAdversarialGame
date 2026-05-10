def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, dict):
            x, y = int(p.get("x", -1)), int(p.get("y", -1))
        else:
            x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    role = str(observation.get("self_role") or observation.get("role") or "")
    is_evader = ("evader" in role.lower()) or ("escape" in role.lower())

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    best_val = -10**18 if is_evader else 10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue

        d = abs(nx - ox) + abs(ny - oy)

        if is_evader:
            # Maximize distance; also bias toward corners away from pursuer and keep stable when equal.
            corner_bias = min(nx, ny) + min(w - 1 - nx, h - 1 - ny)
            away_bias = (nx * (nx - ox) + ny * (ny - oy)) * 1e-3
            stable_bias = -0.01 * (abs(nx - sx) + abs(ny - sy))
            val = d + 0.05 * corner_bias + away_bias + stable_bias
            if val > best_val:
                best_val, best = val, (dx, dy)
        else:
            # Pursuer: minimize distance; reduce chance of giving easy escape by steering toward "cutting off".
            cut = -((nx - ox) * (ny - oy)) * 1e-3
            stable_bias = -0.01 * (abs(nx - sx) + abs(ny - sy))
            val = d + cut + stable_bias
            if val < best_val:
                best_val, best = val, (dx, dy)

    return [int(best[0]), int(best[1])]
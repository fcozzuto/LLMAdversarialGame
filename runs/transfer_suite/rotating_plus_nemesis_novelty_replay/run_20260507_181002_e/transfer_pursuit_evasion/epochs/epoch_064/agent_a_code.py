def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    sr = str(observation.get("self_role", "")).lower()
    orr = str(observation.get("opponent_role", "")).lower()
    evade = ("evader" in sr) or ("runner" in sr) or (("pursuer" not in sr) and ("evader" in orr))

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if evade:
        tx, ty = max(corners, key=lambda c: (c[0] - ox) * (c[0] - ox) + (c[1] - oy) * (c[1] - oy))
    else:
        tx, ty = min(corners, key=lambda c: (c[0] - ox) * (c[0] - ox) + (c[1] - oy) * (c[1] - oy))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        d_op = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        d_tg = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)

        if evade:
            val = d_op + 0.25 * d_tg
        else:
            val = -d_op - 0.10 * d_tg

        if best is None:
            best, best_val = (dx, dy), val
        else:
            if val > best_val:
                best, best_val = (dx, dy), val
            elif val == best_val:
                if abs(dx) + abs(dy) < abs(best[0]) + abs(best[1]):
                    best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]
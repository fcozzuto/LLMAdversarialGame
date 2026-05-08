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

        dist_to_target = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        dist_to_op = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)

        if evade:
            # Run away while still drifting to chosen corner
            val = (dist_to_target, dist_to_op)
            want = (-1, 1)  # maximize target far, minimize opponent close
        else:
            # Chase while controlling opponent-side corner pressure
            val = (dist_to_target, -dist_to_op)
            want = (1, 1)  # minimize target distance, maximize -dist_to_op

        if best is None:
            best = (dx, dy)
            best_val = val
            continue

        # Deterministic lexicographic comparison based on evade/pursue intent
        if evade:
            # maximize dist_to_target, then maximize dist_to_op
            if val[0] > best_val[0] or (val[0] == best_val[0] and val[1] > best_val[1]):
                best, best_val = (dx, dy), val
        else:
            # minimize dist_to_target, then maximize (-dist_to_op) == minimize dist_to_op
            if val[0] < best_val[0] or (val[0] == best_val[0] and val[1] > best_val[1]):
                best, best_val = (dx, dy), val

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]
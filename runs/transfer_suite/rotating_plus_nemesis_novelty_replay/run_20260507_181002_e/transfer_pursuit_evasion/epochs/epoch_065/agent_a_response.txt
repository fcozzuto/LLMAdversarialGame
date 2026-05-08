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
    # Pursuer tries to head into the opponent's closest corner; evader tries to run to the opposite corner.
    if evade:
        tx, ty = max(corners, key=lambda c: (c[0] - ox) * (c[0] - ox) + (c[1] - oy) * (c[1] - oy))
    else:
        tx, ty = min(corners, key=lambda c: (c[0] - ox) * (c[0] - ox) + (c[1] - oy) * (c[1] - oy))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        d2_op = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        d2_corner = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        man = abs(nx - ox) + abs(ny - oy)

        # Score: main objective distance to opponent (min for pursuer, max for evader),
        # secondary: drive toward/away from target corner, tertiary: reduce Manhattan jitter.
        if evade:
            val = d2_op * 100 - d2_corner * 2 - man
        else:
            val = -d2_op * 100 - d2_corner * 2 - man

        if best_val is None or (val > best_val):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
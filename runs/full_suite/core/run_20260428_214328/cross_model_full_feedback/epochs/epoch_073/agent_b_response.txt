def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obst = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    # deterministic small priority: try to grab nearest resource not blocked
    resources = []
    for p in observation.get("resources") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))
    if resources:
        # pick resource with smallest Chebyshev distance; tie break by x then y
        best = None
        bestd = None
        for rx, ry in resources:
            d = max(abs(rx - sx), abs(ry - sy))
            if best is None or d < bestd or (d == bestd and (rx, ry) < best):
                best = (rx, ry)
                bestd = d
        dx = 0 if best[0] == sx else (1 if best[0] > sx else -1)
        dy = 0 if best[1] == sy else (1 if best[1] > sy else -1)
        return [dx, dy]

    # no resources: move toward center while avoiding obstacles and staying in bounds
    cx, cy = w // 2, h // 2
    best_move = (0, 0)
    best_score = -10**9
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
                # prefer closer to center, but also minimal distance to opponent to avoid
                score = - (abs(nx - cx) + abs(ny - cy)) - max(abs(nx - ox), abs(ny - oy))
                if score > best_score:
                    best_score = score
                    best_move = (dx, dy)
    return [best_move[0], best_move[1]]
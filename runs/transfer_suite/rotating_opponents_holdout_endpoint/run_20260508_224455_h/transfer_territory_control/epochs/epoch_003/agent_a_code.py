def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    ox, oy = observation.get("opponent_position", (sx, sy))
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    unclaimed = list(map(tuple, observation.get("unclaimed_cells", [])))
    opp_t = set(map(tuple, observation.get("opponent_territory", [])))

    cx, cy = w // 2 - 1, h // 2 - 1
    center = (max(0, min(w - 1, cx)), max(0, min(h - 1, cy)))

    if unclaimed:
        tx, ty = min(unclaimed, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy) + 2 * (abs(p[0] - center[0]) + abs(p[1] - center[1])))
    elif opp_t:
        tx, ty = min(opp_t, key=lambda p: abs(p[0] - ox) + abs(p[1] - oy) + abs(p[0] - center[0]) + abs(p[1] - center[1]))
    else:
        tx, ty = center

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    bestv = 10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        v = abs(nx - tx) + abs(ny - ty)
        if v < bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]
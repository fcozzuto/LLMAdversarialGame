def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]
    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for dx, dy, nx, ny in valid:
        # Chebyshev distance (diagonal-friendly)
        nd = None
        for rx, ry in resources:
            d = abs(nx - rx)
            e = abs(ny - ry)
            cd = d if d > e else e
            if nd is None or cd < nd:
                nd = cd
        # Prefer reducing distance to resources; tie-break by increasing opponent distance
        od = max(abs(nx - ox), abs(ny - oy))
        key = (-nd, -od, abs(dx) + abs(dy), dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)
    return [int(best[0]), int(best[1])]
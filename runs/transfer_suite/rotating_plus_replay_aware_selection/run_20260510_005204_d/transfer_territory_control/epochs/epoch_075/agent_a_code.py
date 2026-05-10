def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    cx, cy = (w - 1) // 2, (h - 1) // 2

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(1, 0), (0, 1), (-1, 0), (0, -1), (0, 0)]

    best = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if resources:
            d = min(abs(nx - rx) + abs(ny - ry) for rx, ry in resources)
        else:
            d = abs(nx - cx) + abs(ny - cy)
        score = (d, 0 if (dx, dy) == (0, 0) else 1)
        if best_score is None or score < best_score:
            best_score = score
            best = [dx, dy]

    if best is not None:
        return best
    return [0, 0]
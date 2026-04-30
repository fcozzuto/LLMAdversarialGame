def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    resources = []
    for p in (observation.get("resources", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    inside = lambda x, y: 0 <= x < w and 0 <= y < h
    dist = lambda a, b: max(abs(a[0] - b[0]), abs(a[1] - b[1])
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) not in obstacles and (nx, ny) != (ox, oy):
            legal.append((dx, dy))
    if not legal:
        return [0, 0]
    if resources:
        best = None
        bestv = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            d = min(dist((nx, ny), r) for r in resources)
            v = (d, dist((nx, ny), (ox, oy)))
            if best is None or v < bestv:
                best, bestv = (dx, dy), v
        return [best[0], best[1]]
    tx, ty = w // 2, h // 2
    best = min(legal, key=lambda m: dist((sx + m[0], sy + m[1]), (tx, ty)))
    return [best[0], best[1]]
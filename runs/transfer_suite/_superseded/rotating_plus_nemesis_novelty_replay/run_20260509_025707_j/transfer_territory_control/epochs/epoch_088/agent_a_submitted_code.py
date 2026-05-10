def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 1)
    h = observation.get("grid_height", 1)
    obstacles = set(observation.get("obstacles") or [])
    resources = observation.get("resources") or []
    if w <= 0 or h <= 0:
        return [0, 0]

    cx, cy = (w - 1) // 2, (h - 1) // 2

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    target = (cx, cy)
    if resources:
        target = min(resources, key=lambda p: man((sx, sy), p))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        dt = man((nx, ny), target)
        do = man((nx, ny), (ox, oy))
        val = dt * 2 - do
        if bestv is None or val < bestv or (val == bestv and (dx, dy) < best):
            bestv = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]
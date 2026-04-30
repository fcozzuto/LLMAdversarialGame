def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    inside = lambda x, y: 0 <= x < w and 0 <= y < h
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def d(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) not in obstacles:
            if (nx, ny) != (ox, oy):
                legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]
    if resources:
        best = None
        best_score = None
        for dx, dy, nx, ny in legal:
            nearest = min(d((nx, ny), r) for r in resources)
            score = (-nearest, d((nx, ny), (ox, oy)))
            if best_score is None or score < best_score:
                best_score = score
                best = (dx, dy)
        return [int(best[0]), int(best[1])]
    # No resources visible: drift away from opponent deterministically
    best = None
    best_score = None
    for dx, dy, nx, ny in legal:
        score = (d((nx, ny), (ox, oy)), -nx, -ny, dx, dy)  # maximize distance; tie-break
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)
    return [int(best[0]), int(best[1])]
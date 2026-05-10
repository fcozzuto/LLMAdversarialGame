def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    targets = []
    for key in ("resources", "unclaimed_cells"):
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = p[0], p[1]
                if isinstance(x, int) and isinstance(y, int) and inside(x, y):
                    targets.append((x, y))
        if targets:
            break

    if targets:
        if (sx, sy) in obstacles:
            targets = []
    if not targets:
        targets = [(w // 2, h // 2), (ox, oy)]

    tx, ty = min(targets, key=lambda t: manh((sx, sy), t))

    dirs = [(0, -1), (1, 0), (0, 1), (-1, 0)]
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            score = manh((nx, ny), (tx, ty))
            score2 = manh((nx, ny), (ox, oy))
            candidates.append((score, -score2, dx, dy))
    if not candidates:
        return [0, 0]

    candidates.sort()
    _, _, dx, dy = candidates[0]
    return [int(dx), int(dy)]
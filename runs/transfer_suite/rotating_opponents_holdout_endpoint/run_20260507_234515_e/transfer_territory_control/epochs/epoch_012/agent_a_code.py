def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", sp) or sp
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def to_cells(lst):
        out = []
        for p in lst or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                out.append((x, y))
        return out

    obstacles = set(to_cells(observation.get("obstacles", []) or []))
    unclaimed = to_cells(observation.get("unclaimed_cells", []) or [])

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = None

    nearest = None
    if unclaimed:
        nearest = min(unclaimed, key=lambda p: dist((sx, sy), p))

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        score = 0
        if nearest is not None:
            score += -dist((nx, ny), nearest)  # move toward unclaimed
            if (nx, ny) in unclaimed:
                score += 50
        # also try not to approach opponent too much
        score += dist((nx, ny), (ox, oy)) * 0.5
        if best is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best
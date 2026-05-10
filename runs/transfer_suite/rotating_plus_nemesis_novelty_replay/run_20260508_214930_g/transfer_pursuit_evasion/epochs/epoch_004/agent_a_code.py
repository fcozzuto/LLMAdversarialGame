def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        for bx, by in obstacles:
            if bx == x and by == y:
                return True
        return False

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    steps = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = None

    for dx, dy in steps:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or blocked(nx, ny):
            continue
        d_opp = dist2(nx, ny, ox, oy)
        d_res = 0
        if isinstance(resources, list) and resources:
            m = None
            for r in resources:
                if isinstance(r, (list, tuple)) and len(r) >= 2:
                    rx, ry = int(r[0]), int(r[1])
                    if in_bounds(rx, ry) and not blocked(rx, ry):
                        v = dist2(nx, ny, rx, ry)
                        if m is None or v < m:
                            m = v
            if m is not None:
                d_res = m
        score = (-d_opp, d_res, dx, dy)
        if best is None or score < best_score:
            best_score = score
            best = [dx, dy]

    if best is not None:
        return best

    for dx, dy in [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = sx + dx, sy + dy
        if in_bounds(nx, ny) and not blocked(nx, ny):
            return [dx, dy]
    return [0, 0]
def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [7, 7])
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs_set = set((p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) == 2)
    deltas = [[0, 0], [1, 0], [0, 1], [-1, 0], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dsq(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    best = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs_set:
            continue
        capture = 0
        if resources:
            min_d = None
            for rx, ry in resources:
                d = dsq(nx, ny, rx, ry)
                if min_d is None or d < min_d:
                    min_d = d
            if any(nx == rx and ny == ry for rx, ry in resources):
                capture = 1000
            score = capture - min_d + 0.01 * dsq(nx, ny, ox, oy)
        else:
            score = 0.01 * dsq(nx, ny, ox, oy)
        if best is None or score > best_score:
            best = [dx, dy]
            best_score = score
    return best if best is not None else [0, 0]
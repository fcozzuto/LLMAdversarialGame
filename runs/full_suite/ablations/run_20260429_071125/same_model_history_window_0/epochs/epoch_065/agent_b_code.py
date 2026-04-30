def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if resources:
        best = resources[0]
        best_score = dist((ox, oy), best) - dist((sx, sy), best)
        for r in resources[1:]:
            s = dist((ox, oy), r) - dist((sx, sy), r)
            if s > best_score:
                best_score = s
                best = r
        target = best
    else:
        target = (w // 2, h // 2)

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        val = dist((nx, ny), target) * 10 - dist((nx, ny), (ox, oy))
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]
    if best_val is None:
        return [0, 0]
    return best_move
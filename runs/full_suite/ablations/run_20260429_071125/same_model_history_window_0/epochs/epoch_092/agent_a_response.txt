def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation.get('self_position', [0, 0])
    ox, oy = observation.get('opponent_position', [0, 0])
    resources = observation.get('resources', []) or []
    obstacles = observation.get('obstacles', []) or []
    obs_set = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best_t = None
    best_val = None
    for r in resources:
        rx, ry = r
        if (rx, ry) == (sx, sy) or (rx, ry) == (ox, oy):
            continue
        sv = dist((sx, sy), (rx, ry)) - 0.5 * dist((ox, oy), (rx, ry))
        if best_val is None or sv < best_val or (sv == best_val and (rx, ry) < best_t):
            best_val = sv
            best_t = (rx, ry)

    if best_t is None and resources:
        best_t = tuple(resources[0])

    tx, ty = best_t if best_t is not None else (w // 2, h // 2)

    options = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in options:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue
        cur = dist((nx, ny), (tx, ty))
        opp_far = dist((nx, ny), (ox, oy))
        opp_to_target = dist((ox, oy), (tx, ty))
        score = cur + 0.05 * opp_to_target - 0.01 * opp_far
        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    if best_score is None:
        return [0, 0]
    return [best_move[0], best_move[1]]
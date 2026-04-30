def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if in_bounds(nx, ny) and (nx, ny) not in obs:
            valid.append((dx, dy))

    if not valid:
        return [0, 0]

    if not resources:
        best = max(valid, key=lambda d: (man(sx + d[0], sy + d[1], ox, oy), -man(sx + d[0], sy + d[1], sx, sy)))
        return [best[0], best[1]]

    best_res = None
    best_score = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        score = do - ds
        if best_score is None or score > best_score or (score == best_score and ds < man(sx, sy, best_res[0], best_res[1])):
            best_score = score
            best_res = (rx, ry)

    rx, ry = best_res
    cur_best = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        # prefer reducing our distance to the target, then increasing opponent distance
        score = (-man(nx, ny, rx, ry), man(nx, ny, ox, oy))
        if cur_best is None or score > cur_best[0]:
            cur_best = (score, dx, dy)
    return [cur_best[1], cur_best[2]]
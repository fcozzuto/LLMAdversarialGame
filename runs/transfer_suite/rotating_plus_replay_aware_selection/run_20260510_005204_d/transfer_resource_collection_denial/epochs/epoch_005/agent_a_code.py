def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    res_sorted = sorted((rx, ry) for rx, ry in resources)
    best_rx, best_ry = res_sorted[0]
    best_priority = None

    # Pick best contest target based on advantage (opp_dist - my_dist), then nearer resource.
    for rx, ry in res_sorted:
        my_d = md(sx, sy, rx, ry)
        opp_d = md(ox, oy, rx, ry)
        priority = (opp_d - my_d, -my_d, rx, ry)
        if best_priority is None or priority > best_priority:
            best_priority = priority
            best_rx, best_ry = rx, ry

    tx, ty = best_rx, best_ry

    # Evaluate immediate moves: minimize my distance to target while not walking into obstacles;
    # add small bonus for increasing opponent distance to target.
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        my_d = md(nx, ny, tx, ty)
        opp_d = md(ox, oy, tx, ty)
        score = (-my_d, opp_d, nx == tx and ny == ty, -((nx, ny) != (sx, sy)))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
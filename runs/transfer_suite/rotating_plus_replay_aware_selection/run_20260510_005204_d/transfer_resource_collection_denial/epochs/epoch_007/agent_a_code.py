def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cdist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev for 8-dir

    best = None
    for rx, ry in resources:
        my_d = cdist(sx, sy, rx, ry)
        opp_d = cdist(ox, oy, rx, ry)
        pr = (opp_d - my_d, -my_d, -abs(rx - sx) - abs(ry - sy), rx, ry)
        if best is None or pr > best[0]:
            best = (pr, rx, ry)
    _, tx, ty = best

    best_move = (0, 0)
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        my_d = cdist(nx, ny, tx, ty)
        # opponent distance is used as a proxy (opponent assumed to keep pressure on the same target)
        opp_d = cdist(ox, oy, tx, ty)
        # slight preference for moving to reduce distance faster; deterministic tie-break on direction order
        val = (-my_d, opp_d, dx, dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
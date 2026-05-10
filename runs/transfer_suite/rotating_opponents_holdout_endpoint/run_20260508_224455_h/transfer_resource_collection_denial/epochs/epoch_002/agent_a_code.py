def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    obs = set((x, y) for x, y in obstacles)

    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Pick a resource we can reach earlier than the opponent (tie-break by shortest own distance)
    best_tx, best_ty = resources[0]
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        key = (ds - do, ds, rx, ry)  # smaller is better
        if best_key is None or key < best_key:
            best_key = key
            best_tx, best_ty = rx, ry

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        dcur = cheb(sx, sy, best_tx, best_ty)
        dnext = cheb(nx, ny, best_tx, best_ty)
        do_next = cheb(nx, ny, ox, oy)

        # Score: prioritize decreasing distance to target; then maximize opponent distance; then avoid equalities by preferring smaller do_next
        dist_gain = dcur - dnext  # positive is good
        key = (-dist_gain, dnext, -do_next, dx, dy)
        if best_score is None or key < best_score:
            best_score = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
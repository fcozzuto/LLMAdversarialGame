def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    deltas = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]

    def clamp(x, y):
        if x < 0: x = 0
        if x >= w: x = w - 1
        if y < 0: y = 0
        if y >= h: y = h - 1
        return x, y

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # If no visible resources, go to corner farthest from opponent.
    if not resources:
        corners = [(0,0), (0,h-1), (w-1,0), (w-1,h-1)]
        tx, ty = max(corners, key=lambda c: dist(c, (ox, oy)))
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    # Pick resource where we are relatively advantaged: maximize (opp_dist - self_dist).
    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = max(0, dist((sx, sy), (rx, ry)))
        do = max(0, dist((ox, oy), (rx, ry)))
        key = (do - ds, -ds, -do, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # Choose a move delta that reduces distance to target and avoids obstacles.
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = clamp(sx + dx, sy + dy)
        if (nx, ny) in obstacles:
            continue
        ns = dist((nx, ny), (tx, ty))
        # slight bias: also prefer moving away from opponent when tie (denial)
        opps = dist((nx, ny), (ox, oy))
        score = ( -ns, opps, dx, dy )
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    # If all moves are blocked, stay.
    return [int(best_move[0]), int(best_move[1])]
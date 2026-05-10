def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cdist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy  # Chebyshev (8-dir)

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_res = None
    best_key = None

    # Pick a target where we are relatively closer than opponent, but also prefer "more urgent" ones.
    for rx, ry in resources:
        my_d = cdist(sx, sy, rx, ry)
        opp_d = cdist(ox, oy, rx, ry)
        if opp_d == my_d:
            closeness = 0
        else:
            closeness = opp_d - my_d  # positive if we are closer
        urgency = -(my_d)  # nearer to us is generally better
        # Tie-break: prefer resources closer to our side (lower x+y) deterministically.
        side = (rx + ry)
        key = (closeness, urgency, -side, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best_res = (rx, ry)

    tx, ty = best_res
    best_move = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        my_new = cdist(nx, ny, tx, ty)
        opp_now = cdist(ox, oy, tx, ty)

        # Proxy for "denial": make it harder for opponent to reach our chosen target.
        opp_new = cdist(nx, ny, ox, oy)  # how close we are to opponent (prefer not to collide)
        score = (
            -my_new,               # minimize distance to target
            (opp_now - my_new),   # grow our relative advantage to target (proxy)
            -opp_new,              # keep some separation
            -abs(nx - tx) - abs(ny - ty),  # slight additional preference
            nx, ny
        )
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    # Deterministic tie-breakers: prefer higher score, then closer to nearest resource, then lexicographic move.
    best_move = (0, 0)
    best_score = -10**30
    best_dist = 10**30

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        cur_score = -10**30
        nearest_dist = 10**30

        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            if ds == 0 and (nx, ny) == (rx, ry):
                score = 10**12  # capture now
            else:
                lead = do - ds  # positive if we are closer than opponent
                # Race pressure + being closer is good; also mildly prefer resources that opponent can't take immediately.
                score = 3000 * lead - 10 * ds - 2 * (do == 1)
            if score > cur_score:
                cur_score = score
            if ds < nearest_dist:
                nearest_dist = ds

        if (cur_score > best_score) or (cur_score == best_score and (nearest_dist < best_dist or (nearest_dist == best_dist and (dx, dy) < best_move))):
            best_score = cur_score
            best_dist = nearest_dist
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
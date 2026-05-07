def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    res = [(int(x), int(y)) for x, y in resources]

    # Opponent best-case distance to each resource after their next move
    opp_best = {}
    for tx, ty in res:
        best = 10**9
        for dx, dy in moves:
            nx, ny = ox + dx, oy + dy
            if valid(nx, ny):
                d = man(nx, ny, tx, ty)
                if d < best:
                    best = d
        if best == 10**9:
            best = man(ox, oy, tx, ty)
        opp_best[(tx, ty)] = best

    best_move = (0, 0)
    best_margin = -10**18
    best_dist = 10**18

    for dx, dy in sorted(moves):
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Choose the resource where we gain the most closeness vs opponent
        move_best_margin = -10**18
        move_best_dist = 10**18
        for tx, ty in res:
            our_d = man(nx, ny, tx, ty)
            margin = opp_best[(tx, ty)] - our_d
            if margin > move_best_margin or (margin == move_best_margin and our_d < move_best_dist):
                move_best_margin = margin
                move_best_dist = our_d

        if (move_best_margin > best_margin or
            (move_best_margin == best_margin and move_best_dist < best_dist) or
            (move_best_margin == best_margin and move_best_dist == best_dist and (dx, dy) < best_move)):
            best_margin = move_best_margin
            best_dist = move_best_dist
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
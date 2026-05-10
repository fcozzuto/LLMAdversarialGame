def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    turns_remaining = observation.get("turns_remaining", 0)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    # Late game: prioritize immediate pickup; early: prioritize creating distance advantage vs opponent.
    late = 1.0 if turns_remaining <= 10 else 0.0
    early = 1.0 - late

    best_score = -10**18
    best_move = (0, 0)

    # If we are on a resource, stay (pickup assumed).
    for r in resources:
        if r[0] == sx and r[1] == sy:
            return [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        move_score = 0
        # Evaluate best target resource from resulting position.
        # Score combines: (opponent gets farther) and (we get closer), plus slight tie-break for being closer to target.
        for rx, ry in resources:
            d_me = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            adv = d_op - d_me  # positive if we are closer than opponent
            # Encourage moving to a resource even if opponent also close.
            s = early * (200 * adv) + late * (-10 * d_me) + (-d_me)
            if adv >= 0:
                s += 50
            move_score = s if s > move_score else move_score
        # If tied, choose move that minimizes our distance to closest resource (deterministic).
        if move_score > best_score:
            best_score = move_score
            best_move = (dx, dy)
        elif move_score == best_score:
            # Deterministic tie-break: smaller cheb to nearest resource, then lexicographic dx,dy
            def nearest_dist(x, y):
                md = 10**9
                for rx, ry in resources:
                    d = cheb(x, y, rx, ry)
                    if d < md:
                        md = d
                return md
            nd_best = nearest_dist(sx + best_move[0], sy + best_move[1])
            nd_new = nearest_dist(nx, ny)
            if nd_new < nd_best:
                best_move = (dx, dy)
            elif nd_new == nd_best:
                if (dx, dy) < best_move:
                    best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
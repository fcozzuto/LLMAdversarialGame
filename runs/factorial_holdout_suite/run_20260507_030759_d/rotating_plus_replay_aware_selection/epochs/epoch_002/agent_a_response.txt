def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((x, y) for x, y in observation["obstacles"])
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny): 
                continue
            d = cheb(nx, ny, tx, ty)
            if best is None or d < best[0]:
                best = (d, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    # Strategic change: evaluate moves by (1) picking a target we are likely to beat,
    # (2) prefer moves that reduce the gap further and avoid "opponent-shadowing".
    best_move = (None, None, None)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Choose target deterministically based on our advantage from the prospective position.
        best_target = None
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Gap-first: we want ds much smaller than do; break ties by smaller ds.
            # Add small bias toward resources closer to center to reduce corner trapping.
            center_bias = -((rx - (w - 1) / 2) ** 2 + (ry - (h - 1) / 2) ** 2) * 1e-6
            score = (do - ds, -ds) + (center_bias,)
            if best_target is None or score > best_target[0] or (score == best_target[0] and (rx, ry) < best_target[1]):
                best_target = (score, (rx, ry), ds, do)

        # Opponent-response: if opponent is very close to our chosen target, prioritize taking
        # a different target by increasing a penalty with their proximity.
        rx, ry = best_target[1]
        ds, do = best_target[2], best_target[3]
        gap = do - ds
        opp_penalty = 0 if do >= ds + 2 else (2 - (do - ds)) * 0.01
        # Also discourage stepping away from *any* good resource when we are near one.
        nearby = 1e9
        for r2x, r2y in resources:
            d2 = cheb(nx, ny, r2x, r2y)
            if d2 < nearby:
                nearby = d2
        away_penalty = nearby * 1e-3

        final = (gap, -ds, -do, -(opp_penalty + away_penalty))
        if best_move[0] is None or final > best_move[0]:
            best_move = (final, dx, dy)

    return [best_move[1], best_move[2]] if best_move[0] is not None else [0, 0]
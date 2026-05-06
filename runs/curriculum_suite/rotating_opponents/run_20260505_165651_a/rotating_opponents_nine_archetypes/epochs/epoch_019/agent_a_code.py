def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Infer opponent's likely target: closest resource to opponent.
    opp_closest = None
    opp_best_d = None
    for rx, ry in resources:
        d = king_dist(ox, oy, rx, ry)
        if opp_best_d is None or d < opp_best_d:
            opp_best_d = d
            opp_closest = (rx, ry)

    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0

    best = None  # (key, dx, dy)
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not inb(nx, ny):
            continue

        # Evaluate a move by how much it can beat the opponent on some resource,
        # while avoiding the resource the opponent is most likely heading to.
        best_margin = -10**9
        alt_penalty = 0.0
        for rx, ry in resources:
            ds = king_dist(nx, ny, rx, ry)
            do = king_dist(ox, oy, rx, ry)
            margin = do - ds  # positive means we arrive no later than opponent
            # Discourage going for opponent's probable target unless we can win it clearly.
            if opp_closest == (rx, ry) and margin < 1:
                margin -= 3
            # Encourage taking a resource that is not the "obvious" one for opponent.
            if opp_closest != (rx, ry) and opp_best_d is not None:
                alt_penalty += 0.005 * (king_dist(ox, oy, rx, ry) - opp_best_d)
            if margin > best_margin:
                best_margin = margin

        # Secondary terms: avoid being stuck behind overall and mildly centralize.
        self_to_center = abs(nx - cx) + abs(ny - cy)
        opp_adv_if_here = min((king_dist(ox, oy, rx, ry) - king_dist(nx, ny, rx, ry)) for rx, ry in resources)

        # Key: maximize winning margin; then minimize our distance to nearest resource; then minimize opponent advantage.
        nearest_self_d = min(king_dist(nx, ny, rx, ry) for rx, ry in resources)
        key = (-(best_margin - 0.05 * self_to_center + 0.1 * alt_penalty),
               nearest_self_d,
               -(opp_adv_if_here))

        if best is None or key < best[0]:
            best = (key, dxm, dym)

    return [best[1], best[2]] if best else [0, 0]
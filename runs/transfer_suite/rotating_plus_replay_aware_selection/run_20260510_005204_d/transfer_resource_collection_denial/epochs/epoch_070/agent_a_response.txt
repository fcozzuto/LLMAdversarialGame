def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    best = None
    best_move = (0, 0)

    # Precompute opponent distances to each resource
    opp_dists = [(r[0], r[1], cheb(ox, oy, r[0], r[1])) for r in resources]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Choose the resource that gives the largest "contestation advantage" after this move
        # Tie-breaks: higher advantage, closer to that resource, and less closeness to opponent.
        top_adv = -10**9
        top_myd = 10**9
        top_rx = top_ry = 0

        min_myd_any = 10**9
        for rx, ry, opd in opp_dists:
            myd = cheb(nx, ny, rx, ry)
            if myd < min_myd_any:
                min_myd_any = myd
            adv = opd - myd
            if adv > top_adv or (adv == top_adv and (myd < top_myd or (myd == top_myd and (rx < top_rx or (rx == top_rx and ry < top_ry))))):
                top_adv, top_myd, top_rx, top_ry = adv, myd, rx, ry

        # Discourage giving the opponent a too-easy chase into our immediate area
        opp_close = cheb(nx, ny, ox, oy)
        utility = (top_adv, -top_myd, -opp_close, -min_myd_any, top_rx, top_ry)
        if best is None or utility > best:
            best = utility
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
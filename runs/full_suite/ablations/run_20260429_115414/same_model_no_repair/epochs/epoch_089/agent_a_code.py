def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation["grid_width"]
    h = observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    if not resources:
        return [0, 0]

    obs = {(p[0], p[1]) for p in obstacles}
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Find resource we are best positioned to secure, or best to contest if opponent is closer.
    best_res = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obs:
            continue
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Prefer: (a) resources we can reach no later than opponent; (b) otherwise least-worse contest.
        winable = 1 if myd <= opd else 0
        # Key: higher winable, then maximize (opd-myd), then smaller myd, then deterministic tie on position.
        key = (winable, opd - myd, -myd, -rx * 8 - ry)
        if best_key is None or key > best_key:
            best_key = key
            best_res = (rx, ry)

    if best_res is None:
        return [0, 0]
    rx, ry = best_res

    # Score candidate moves by improvement toward chosen target and reduction of opponent advantage.
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue

        myd = cheb(nx, ny, rx, ry)
        opd = cheb(ox, oy, rx, ry)

        # If opponent is currently closer, also try to move into "denial" range (parity-like).
        denial = 0
        if myd <= opd:
            denial = 5000
        elif myd == opd + 1:
            denial = 500

        # Small additional preference: don't walk away from best target.
        cur_myd = cheb(sx, sy, rx, ry)
        advance = cur_myd - myd  # positive if we get closer
        score = (opd - myd) * 200 + denial + advance * 50 - myd

        # Deterministic tie-break: prefer moves with smaller dx, then dy.
        tie = (dx * 10 + dy)
        score_tuple = (score, -tie)

        if best_score is None or score_tuple > best_score:
            best_score = score_tuple
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]
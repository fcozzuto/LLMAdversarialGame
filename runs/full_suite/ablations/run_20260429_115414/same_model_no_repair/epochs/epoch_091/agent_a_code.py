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

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def pick_target():
        # Resource most likely targeted by opponent (closest in Chebyshev distance).
        best = None
        bestv = 10**9
        for r in resources:
            v = cheb(ox, oy, r[0], r[1])
            if v < bestv:
                bestv, best = v, r
        return best

    tgt = pick_target()

    # Evaluate each possible move by relative advantage on resources, with a bias to contest opponent's target.
    best_move = (0, 0, -10**18)  # (dx, dy, score)
    parity_bias = (observation.get("turn_index", 0) & 1) * 1e-6
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        # Base: prevent falling behind everywhere by considering best contest.
        best_adv = -10**18
        best_my = 10**18
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = opd - myd  # positive means we are closer after the move
            if adv > best_adv:
                best_adv = adv
            if myd < best_my:
                best_my = myd

        # Contest bias: explicitly reduce distance to opponent's likely target.
        bias = 0
        if tgt is not None:
            bias = 0.5 * (cheb(ox, oy, tgt[0], tgt[1]) - cheb(nx, ny, tgt[0], tgt[1]))

        # Score combines: maximize advantage, then minimize our distance to nearest resource.
        score = best_adv * 2.0 + bias - 0.15 * best_my + parity_bias
        # Deterministic tie-break: prefer moves that are lexicographically smaller among equal scores.
        if score > best_move[2] or (score == best_move[2] and (dx, dy) < (best_move[0], best_move[1])):
            best_move = (dx, dy, score)

    return [int(best_move[0]), int(best_move[1])]
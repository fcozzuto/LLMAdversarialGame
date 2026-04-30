def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    t = observation.get("turn_index", 0)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    res = [(x, y) for (x, y) in resources if inb(x, y) and (x, y) not in obstacles]
    if not res:
        best = None
        bestv = -10**18
        for dx, dy, nx, ny in legal:
            v = cheb(nx, ny, ox, oy) + 0.01 * (nx + ny) - 0.001 * (t % 7)
            if v > bestv:
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    # Dynamic target preference: alternate between closest-to-opponent and farthest-from-opponent clusters.
    want_close_to_opp = (t % 2 == 1)
    best = None
    bestv = -10**18

    for dx, dy, nx, ny in legal:
        # Immediate pickup bonus
        pickup = 6.0 if (nx, ny) in obstacles else 0.0
        if (nx, ny) in set(res):
            pickup = 100.0

        # Find best resource to go for
        best_r_val = -10**18
        for rx, ry in res:
            d_me = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # If opponent can arrive first, this resource becomes denial value rather than race value.
            # Use different emphasis based on parity to avoid repeating same policy.
            if want_close_to_opp:
                race_bias = -0.35 * d_op
            else:
                race_bias = 0.25 * cheb(rx, ry, ox, oy)
            # Denial term: prefer resources where we are not behind.
            behind = d_me - d_op
            denial = 0.0
            if behind < 0:
                denial = 3.5 - 0.4 * d_me
            else:
                denial = -1.6 * behind

            # Earlier resources and fewer steps are better.
            rscore = race_bias - 1.1 * d_me + denial
            if rscore > best_r_val:
                best_r_val = rscore

        # Secondary: prefer moves that keep distance from opponent unless we're racing a denial lane
        dist_opp = cheb(nx, ny, ox, oy)
        keep_away = (0.35 if not want_close_to_opp else -0.15) * dist_opp

        # Tie-break deterministically: prefer staying away from obstacles' vicinity by mild penalty
        prox_pen = 0.0
        for ax, ay in obstacles:
            if cheb(nx, ny, ax, ay) == 0:
                prox_pen -= 5.0
            elif cheb(nx, ny, ax, ay) == 1:
                prox_pen -= 0.2

        v = pickup + best_r_val + keep_away + prox_pen
        # Deterministic tie-break: smaller (dx,dy) lexicographically
        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv, best = v, (dx, dy)

    return [best[0], best[1]]
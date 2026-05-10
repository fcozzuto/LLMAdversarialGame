def choose_move(observation):
    gw = int(observation["grid_width"])
    gh = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = {(int(p[0]), int(p[1])) for p in obstacles}
    res_set = {(int(r[0]), int(r[1])) for r in resources}

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def dist8(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        return [0, 0]

    def best_opponent_step(tx, ty, cx, cy):
        # Opponent greedily minimizes dist to target (ties: deterministic)
        best = (cx, cy)
        bestd = 10**9
        bestdx = 0; bestdy = 0
        for dx, dy in moves:
            nx, ny = cx + dx, cy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            d = dist8(nx, ny, tx, ty)
            if d < bestd:
                bestd = d
                best = (nx, ny)
                bestdx, bestdy = dx, dy
        return bestdx, bestdy

    # Deterministic tie-break: sort resources
    rlist = sorted([(int(r[0]), int(r[1])) for r in resources])
    best_move = (0, 0)
    best_score = -10**18

    for dx0, dy0 in moves:
        nx0, ny0 = sx + dx0, sy + dy0
        if not inb(nx0, ny0) or (nx0, ny0) in obs:
            continue
        self_gain = 0
        if (nx0, ny0) in res_set:
            self_gain += 50  # strong immediate collection bias

        # Choose target resource based on one-step competitive advantage
        local_best = -10**18
        for tx, ty in rlist:
            odx, ody = best_opponent_step(tx, ty, ox, oy)
            nox, noy = ox + odx, oy + ody
            if not inb(nox, noy) or (nox, noy) in obs:
                nox, noy = ox, oy

            d_self = dist8(nx0, ny0, tx, ty)
            d_opp = dist8(nox, noy, tx, ty)

            # Prefer resources closer to us, and prevent giving opponent an advantage
            score = (d_opp - d_self) + self_gain
            # Small preference for nearer overall to speed tempo
            score += -0.01 * (d_self + d_opp)
            if score > local_best:
                local_best = score

        if local_best > best_score:
            best_score = local_best
            best_move = (dx0, dy0)
        elif local_best == best_score:
            # deterministic tie-break: lexicographic
            if (dx0, dy0) < best_move:
                best_move = (dx0, dy0)

    dx, dy = best_move
    return [int(dx), int(dy)]
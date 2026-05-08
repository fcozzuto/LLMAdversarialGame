def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_mv = [0, 0]

    # Compute nearest "advantage" resources
    # advantage: self can arrive no later than opponent by margin
    targets = []
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        advantage = od - sd
        targets.append((advantage, sd, od, rx, ry))

    # Prefer resources we can secure; if none, move to contest the most dangerous one (opponent closest)
    targets.sort(key=lambda t: (-t[0], t[1], t[2]))
    can_secure = [t for t in targets if t[0] >= 1]
    focus = can_secure[0] if can_secure else min(targets, key=lambda t: t[2])  # smallest opponent distance

    _, _, _, tx, ty = focus

    # If opponent is already extremely close to its nearest resource, bias toward blocking that resource
    if not can_secure:
        # choose direction that reduces opponent's distance to their closest resource the most
        opp_closest = min(targets, key=lambda t: t[2])
        _, _, _, btx, bty = opp_closest
    else:
        btx, bty = tx, ty

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # main score: increase our progress to chosen target, but discourage moves that give opponent bigger lead
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        lead_after = opd - myd  # positive favors us

        # secondary: if contesting (no secure), reduce opponent advantage toward their target
        if can_secure:
            block_term = 0
        else:
            myd2 = cheb(nx, ny, btx, bty)
            opd2 = cheb(ox, oy, btx, bty)
            # higher is better for us => smaller opponent lead after move
            block_term = (opd2 - myd2)

        # tie-break deterministic: larger lead_after, then smaller myd, then larger myd2 reduction, then closest to opponent to deny
        val = (-lead_after, myd, block_term, cheb(nx, ny, ox, oy))
        if best is None or val < best:
            best = val
            best_mv = [dx, dy]

    return best_mv
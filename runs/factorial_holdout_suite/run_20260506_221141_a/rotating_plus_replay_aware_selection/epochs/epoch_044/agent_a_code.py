def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx = (gw - 1) // 2
        ty = (gh - 1) // 2
        best = [0, 0]
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = -cheb(nx, ny, tx, ty)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    # Pick a resource likely to be ours earlier than opponent.
    best_r = None
    best_score = -10**18
    for rx, ry in resources:
        d_me = cheb(sx, sy, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        # Prefer shorter for us; punish opponent being sooner.
        # Slight tie preference: if we can arrive no later, prioritize.
        score = (d_op - d_me) * 2 - d_me
        if score > best_score:
            best_score = score
            best_r = (rx, ry)

    rx, ry = best_r
    # Choose a legal next move that maximizes improvement toward target,
    # and also discourages stepping into near-opponent denial pressure.
    best = [0, 0]
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d_cur = cheb(sx, sy, rx, ry)
        d_next = cheb(nx, ny, rx, ry)
        toward = d_cur - d_next  # positive if closer
        # If we can collect this turn, prioritize strongly.
        collect_bonus = 5 if (nx, ny) == (rx, ry) else 0
        # Opponent pressure: if we move to make us comparatively slower vs them.
        opp_next_d = cheb(ox, oy, rx, ry)
        # Prefer moves that keep our lead (d_op - d_me) large.
        lead = (opp_next_d - d_next)
        v = toward * 3 + collect_bonus + lead * 0.5
        if v > bestv:
            bestv = v
            best = [dx, dy]
    return best
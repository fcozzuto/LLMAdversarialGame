def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    res = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    # If no resources, move to reduce distance to opponent's corner (deterministic fallback)
    if not res:
        tx, ty = (w - 1, 0) if (ox <= w//2) else (0, h - 1)
        best = (None, -10**9)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            sc = -cheb(nx, ny, tx, ty) - 0.01*(nx + ny)
            if sc > best[1]:
                best = ((dx, dy), sc)
        if best[0] is None:
            return [0, 0]
        return [best[0][0], best[0][1]]

    # Choose a target that we can reach before opponent; then pick move maximizing next-step advantage.
    def target_score(px, py, tx, ty):
        ds = cheb(px, py, tx, ty)
        do = cheb(ox, oy, tx, ty)
        adv = do - ds  # positive means we are closer or equal
        # Prefer advantage, then closeness to the target, then prefer nearer "center of play"
        center_bias = -abs(tx - (w - 1) / 2.0) - abs(ty - (h - 1) / 2.0)
        return adv * 1000 - ds * 10 + center_bias

    # Pick best target from current position
    best_t = res[0]
    best_ts = -10**18
    for tx, ty in res:
        sc = target_score(sx, sy, tx, ty)
        if sc > best_ts or (sc == best_ts and (tx, ty) < best_t):
            best_ts, best_t = sc, (tx, ty)
    tx, ty = best_t

    # One-step lookahead: for each move, re-evaluate our advantage to the chosen target,
    # also slightly reward moves that block by increasing opponent distance to our next cell.
    best_move = (0, 0)
    best_sc = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds_now = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)
        adv = do - ds_now
        # "commitment": if we can take target sooner, boost; otherwise use progress toward it.
        commit = 1 if adv >= 0 else 0
        opp_next = cheb(ox, oy, nx, ny)
        sc = adv * 1000 + commit * 50 - ds_now * 10 + opp_next * 0.1 - 0.01*(nx + ny)
        if sc > best_sc:
            best_sc = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
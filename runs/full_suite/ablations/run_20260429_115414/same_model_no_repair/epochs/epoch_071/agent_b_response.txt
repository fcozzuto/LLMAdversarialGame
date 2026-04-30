def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obst_proximity(x, y):
        best = 99
        for ax, ay in obstacles:
            d = cheb(x, y, ax, ay)
            if d < best: best = d
        return best

    def dist_heur(x, y, rx, ry):
        # obstacle-aware distance: chebyshev + penalty for being near obstacles
        d = cheb(x, y, rx, ry)
        bp = obst_proximity(x, y)
        if bp == 0:
            return 10**6
        if bp == 1:
            d += 2
        return d

    # Target: choose resource maximizing reachable advantage, with obstacle-aware reach time.
    best_t = None
    best_score = -10**18
    for rx, ry in resources:
        ds = dist_heur(sx, sy, rx, ry)
        do = dist_heur(ox, oy, rx, ry)
        # prefer resources we can reach sooner; if tied, prefer ones closer to us
        s = (do - ds) * 3 - ds + (2 if cheb(sx, sy, rx, ry) == 0 else 0) - (1 if cheb(ox, oy, rx, ry) == 0 else 0)
        if s > best_score:
            best_score = s
            best_t = (rx, ry)

    if best_t is None:
        best_t = (w // 2, h // 2)
    tx, ty = best_t

    # If a resource is adjacent, prioritize stepping onto it.
    best_adj = None
    best_adj_rank = -10**18
    for rx, ry in resources:
        d = cheb(sx, sy, rx, ry)
        if d <= 1:
            rank = 10 - d - cheb(ox, oy, rx, ry)
            if rank > best_adj_rank:
                best_adj_rank = rank
                best_adj = (rx, ry)
    if best_adj is not None:
        tx, ty = best_adj

    # Evaluate our immediate next move.
    def is_blocked(nx, ny): return not inb(nx, ny) or (nx, ny) in obstacles

    def opponent_pressure(nx, ny):
        # Encourage moves that reduce opponent's ability to contest the target immediately.
        # Approx: compare opponent distance after we move vs before.
        d0 = cheb(ox, oy, tx, ty)
        # best-case opponent response from their current pos: they can reach any neighbor
        best_opp = 10**9
        for dx, dy in deltas:
            ax, ay = ox + dx, oy + dy
            if inb(ax, ay) and (ax, ay) not in obstacles:
                dd = cheb(ax, ay, tx, ty)
                if dd < best_opp: best_opp = dd
        # Prefer increasing their remaining distance and reducing our distance simultaneously.
        return (d0 - best_opp)

    best_delta = (0, 0)
    best_move_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if is_blocked(nx, ny):
            continue
        myd = dist_
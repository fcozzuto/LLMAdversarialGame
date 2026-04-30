def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []
    obstacles = set((int(p[0]), int(p[1])) for p in obstacles_raw)

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2): 
        dx = x1 - x2; dy = y1 - y2
        return dx if dx >= 0 else -dx if dy == 0 else 0  # overwritten below

    def dist(a, b):
        dx = a[0] - b[0]; dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev (8-neighbor)

    # Pick a target resource: maximize (opponent disadvantage) and our reachability.
    best_t = None
    best_val = -10**18
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not valid(rx, ry): 
            continue
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        # Prefer resources we can reach while opponent isn't closer by much; also prefer closer ones.
        val = (do - ds) * 100 - ds
        if val > best_val:
            best_val = val
            best_t = (rx, ry)

    if best_t is None:
        # Fallback: run directly away from opponent and toward corner (deterministic).
        # Choose corner opposite of opponent to create contention.
        corners = [(0,0),(0,h-1),(w-1,0),(w-1,h-1)]
        tx, ty = corners[0]
        do_min = 10**9
        for cx, cy in corners:
            d = dist((ox, oy), (cx, cy))
            if d < do_min:
                do_min = d; tx, ty = cx, cy
        best_t = (tx, ty)

    tx, ty = best_t

    # Strategic tweak: if opponent is adjacent to target and we are not, contest by moving to reduce distance to target strongly.
    op_to_target = dist((ox, oy), (tx, ty))
    contest = 1 if op_to_target <= 1 else 0

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds_new = dist((nx, ny), (tx, ty))
        # Approximate opponent move impact by assuming opponent stays; deterministic bias to avoid oscillations.
        do_cur = dist((ox, oy), (tx, ty))
        # Bonus if we step closer than we were.
        ds_cur = dist((sx, sy), (tx, ty))
        closer = ds_cur - ds_new

        # Repel from being too close to opponent unless we're contesting.
        d_opp = dist((nx, ny), (ox, oy))
        opp_pen = (0 if contest else max(0, 1 - d_opp) * 200) + (max(0, 2 - d_opp) * 20)

        # Slight deterministic preference for advancing diagonally when tied.
        diag_bonus = 3 if dx != 0 and dy !=
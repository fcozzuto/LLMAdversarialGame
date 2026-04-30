def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1),  (0, 0),  (0, 1),
             (1, -1),  (1, 0),  (1, 1)]

    def valid(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    if not resources:
        # Move to reduce opponent distance (escape) deterministically
        best = (10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            d = cheb(nx, ny, ox, oy)
            key = (d, abs(nx - sx) + abs(ny - sy), nx, ny)
            if key < best:
                best = key
                best_move = [dx, dy]
        return best_move if 'best_move' in locals() else [0, 0]

    # Choose a target that maximizes current advantage (opp farther - self farther)
    best_adv = -10**9
    tx = ty = resources[0][0], resources[0][1]
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        adv = opd - myd
        if adv > best_adv or (adv == best_adv and (rx, ry) < (tx, ty)):
            best_adv = adv
            tx, ty = rx, ry

    # Score each move by how it changes advantage toward the chosen target,
    # and lightly penalize allowing opponent to get relatively closer.
    best_key = None
    best_move = [0, 0]
    cur_m = cheb(sx, sy, tx, ty)
    cur_o = cheb(ox, oy, tx, ty)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cur_o  # opponent position unchanged this turn
        lead = (opd - myd)  # higher is better
        # Opponent relative distance effect: penalize if we move away from target
        move_cost = myd - cur_m
        # Mild obstacle safety: prefer not to be adjacent to obstacle (deterministic small term)
        adj_obs = 0
        for ex in (-1, 0, 1):
            for ey in (-1, 0, 1):
                if ex == 0 and ey == 0:
                    continue
                px, py = nx + ex, ny + ey
                if (px, py) in obstacles:
                    adj_obs += 1
        # Tie-break deterministically by coordinates
        key = (-lead, move_cost, adj_obs, abs(dx) + abs(dy), nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move
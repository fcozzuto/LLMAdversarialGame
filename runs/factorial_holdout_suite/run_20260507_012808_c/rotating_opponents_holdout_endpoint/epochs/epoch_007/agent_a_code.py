def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (0, 0, -10**9)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or ny < 0 or nx >= w or ny >= h: 
                continue
            if (nx, ny) in obstacles: 
                continue
            v = -cheb(nx, ny, tx, ty)
            if v > best[2]:
                best = (dx, dy, v)
        return [best[0], best[1]]

    best_r = None
    best_key = (-10**18, 10**18, 10**18)
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources where we can reach much sooner (or opponent is far).
        adv = (do - ds)
        key = (adv, ds, cheb(rx, ry, 0, 0) + cheb(rx, ry, w - 1, h - 1))
        # Deterministic tie-break: larger adv, then smaller ds, then smaller "centrality distance".
        if key[0] > best_key[0] or (key[0] == best_key[0] and (key[1] < best_key[1] or (key[1] == best_key[1] and key[2] < best_key[2]))):
            best_key = key
            best_r = (rx, ry)
    tx, ty = best_r

    # Choose a legal move that maximizes immediate contest after stepping (distance-based, deterministic).
    best = (0, 0, -10**18)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        ns = cheb(nx, ny, tx, ty)
        no = cheb(ox, oy, tx, ty)
        # Slight preference for reducing our distance; punish giving opponent a lead.
        v = (no - ns) * 10 - ns
        if v > best[2]:
            best = (dx, dy, v)

    # If somehow no move was legal (shouldn't happen), stay.
    if best[2] == -10**18:
        return [0, 0]
    return [best[0], best[1]]
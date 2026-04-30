def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obs = set(tuple(p) for p in observation.get("obstacles", []) or [])
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Target: maximize (op_dist - our_dist), then prefer smaller our_dist, then tie by position.
    best_t = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obs:
            continue
        us = cheb(sx, sy, rx, ry)
        op = cheb(ox, oy, rx, ry)
        key = (-(op - us), us, rx * 8 + ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)
    if best_t is None:
        best_t = tuple(resources[0])
    tx, ty = best_t

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_mv = (0, 0)
    best_sc = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        usn = cheb(nx, ny, tx, ty)
        opponent_can_take = cheb(ox, oy, tx, ty)
        # Score favors reducing our distance, and discourages moving toward a target where opponent is not far behind.
        sc = (usn * 5 + opponent_can_take * 1.5) - (cheb(sx, sy, tx, ty) - usn) * 2
        # If we land on a resource, strongly prefer it.
        if (nx, ny) in resources:
            sc -= 1e6
        # Small preference for staying away from obstacles by requiring legal neighbors around us to be available.
        legal_neighbors = 0
        for ddx, ddy in deltas:
            ax, ay = nx + ddx, ny + ddy
            if inb(ax, ay) and (ax, ay) not in obs:
                legal_neighbors += 1
        sc -= legal_neighbors * 0.05
        if best_sc is None or sc < best_sc:
            best_sc = sc
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]
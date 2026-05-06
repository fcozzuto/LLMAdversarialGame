def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = {(p[0], p[1]) for p in obstacles}

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx; dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    def edge_dist(x, y):
        a = x if x < w - 1 - x else w - 1 - x
        b = y if y < h - 1 - y else h - 1 - y
        return a if a < b else b

    # If no resources, drift to interior while keeping away from opponent.
    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): 
                continue
            score = edge_dist(nx, ny) - 0.01 * cheb(nx, ny, ox, oy)
            if best is None or score > best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    we_edge = edge_dist(sx, sy)
    opp_edge = edge_dist(ox, oy)
    prefer_interior = 1 if we_edge > opp_edge else 0

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        opp_keep = -0.08 * cheb(nx, ny, ox, oy)
        interior_bias = (0.06 * edge_dist(nx, ny)) if prefer_interior else 0.0

        # Target resource that we can most outpace from next position; if none, minimize loss.
        best_delta = None
        best_tiebreak = None
        for rx, ry in resources:
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            delta = d_opp - d_self  # positive means we are closer now than opponent is
            tb = (d_self, d_opp, rx, ry)
            if best_delta is None or delta > best_delta or (delta == best_delta and tb < best_tiebreak):
                best_delta = delta
                best_tiebreak = tb

        # Encourage positive delta strongly; fall back to being closer even if both are losing.
        score = (2.5 * best_delta) + opp_keep + interior_bias + (-0.02 * best_tiebreak[0])
        if best is None or score > best[0]:
            best = (score, dx, dy)

    return [best[1], best[2]] if best else [0, 0]
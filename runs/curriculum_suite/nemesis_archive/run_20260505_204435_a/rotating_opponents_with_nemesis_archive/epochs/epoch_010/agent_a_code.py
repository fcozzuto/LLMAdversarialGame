def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = {(p[0], p[1]) for p in obstacles}

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    def cheb(ax, ay, bx, by):
        dx = ax - bx; dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def center_bias(x, y):
        cx = (w - 1) / 2.0; cy = (h - 1) / 2.0
        dx = (x - cx); dy = (y - cy)
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx + dy

    # No resources: retreat from opponent and drift toward center.
    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            score = -cheb(nx, ny, ox, oy) - 0.2 * center_bias(nx, ny)
            if best is None or score > best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    # With resources: choose a move that maximizes advantage vs opponent for a target resource.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        self_edge = cheb(nx, ny, ox, oy)  # closer to opponent hurts (shadow), so penalize
        local = -10**9
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Want ds smaller than do; also prefer resources that are not too far from us.
            adv = (do - ds)
            local_score = 2.0 * adv - 0.15 * ds - 0.03 * self_edge
            if local_score > local:
                local = local_score
        if best is None or local > best[0]:
            best = (local, dx, dy)

    return [best[1], best[2]] if best else [0, 0]
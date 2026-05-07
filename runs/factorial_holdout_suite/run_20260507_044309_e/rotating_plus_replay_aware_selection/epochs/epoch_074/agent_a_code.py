def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    if not resources:
        tx, ty = w // 2, h // 2
    else:
        best = None
        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Primary: maximize (opponent advantage we deny) => do-ds higher is better.
            # Secondary: minimize our distance; tertiary: prefer higher row (smaller y) deterministically.
            key = (do - ds, -ds, -(ry <= oy), -rx, ry)
            if best is None or key > best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1] if best else (w // 2, h // 2)

    # Local move choice: avoid obstacles, prefer moving closer to target; include tie-break to avoid opponent.
    bestm = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        ns = cheb(nx, ny, tx, ty)
        nos = cheb(nx, ny, ox, oy)
        dist_to_res_now = cheb(sx, sy, tx, ty)
        # If we reduce distance to target, good; also prefer moves that keep away from opponent a bit.
        score = (dist_to_res_now - ns, -ns, nos, -nx, -ny, dx, dy)
        if bestm is None or score > bestm[0]:
            bestm = (score, (dx, dy))
    return [bestm[1][0], bestm[1][1]] if bestm else [0, 0]
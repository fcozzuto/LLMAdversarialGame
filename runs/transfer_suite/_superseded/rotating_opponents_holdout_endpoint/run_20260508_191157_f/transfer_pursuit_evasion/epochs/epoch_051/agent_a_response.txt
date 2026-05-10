def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obs_list = observation.get("obstacles") or []
    obs = set((x, y) for x, y in obs_list)

    role = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role)
    is_pursuer = ("pursuer" in role) or ("chaser" in role)
    if not (is_evader or is_pursuer):
        is_pursuer = True

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def cheb(x, y, tx, ty):
        dx = x - tx
        if dx < 0: dx = -dx
        dy = y - ty
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj_obstacles(x, y):
        c = 0
        for nx in (x - 1, x, x + 1):
            if nx < 0 or nx >= w:
                continue
            for ny in (y - 1, y, y + 1):
                if ny < 0 or ny >= h:
                    continue
                if (nx, ny) in obs:
                    c += 1
        return c

    # Evader: run to farthest corner, with obstacle/escape-line bias
    # Pursuer: minimize distance to evader, with obstacle avoidance and "cut-off" (target reflection)
    if is_evader:
        tx, ty = max(corners, key=lambda c: cheb(ox, oy, c[0], c[1]))
        def score(nx, ny):
            if (nx, ny) in obs:
                return -10**9
            d = cheb(nx, ny, tx, ty)
            od = adj_obstacles(nx, ny)
            # also increase distance from opponent
            dist_from_opp = cheb(nx, ny, ox, oy)
            return d * 3 + dist_from_opp - od * 2
    else:
        # reflect target one step past opponent away from pursuer to encourage intercept
        rx = ox + (1 if ox < sx else -1 if ox > sx else 0)
        ry = oy + (1 if oy < sy else -1 if oy > sy else 0)
        if not in_bounds(rx, ry):
            rx, ry = ox, oy
        tx, ty = rx, ry
        def score(nx, ny):
            if (nx, ny) in obs:
                return -10**9
            d = cheb(nx, ny, ox, oy)
            aim = cheb(nx, ny, tx, ty)
            od = adj_obstacles(nx, ny)
            # prefer moves that reduce cheb to opponent, then reduce aim, then avoid clutter
            return -d * 5 - aim * 2 - od

    best = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            # engine clamps; still treat out-of-bounds move as likely clamped and evaluate by clamped position
            nx = 0 if nx < 0 else w - 1
            ny = 0 if ny < 0 else h - 1
        sc = score(nx, ny)
        if best is None or sc > best:
            best = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
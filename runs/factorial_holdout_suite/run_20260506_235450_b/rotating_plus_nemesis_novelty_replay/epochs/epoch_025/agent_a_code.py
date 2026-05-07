def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def step_towards(tx, ty, x, y):
        return (0 if tx == x else (1 if tx > x else -1),
                0 if ty == y else (1 if ty > y else -1))

    def cell_score(cx, cy):
        if not resources:
            tx, ty = (w - 1) // 2, (h - 1) // 2
            dx, dy = abs(tx - cx), abs(ty - cy)
            return -(dx + dy)
        best = -10**18
        for rx, ry in resources:
            self_d = abs(rx - cx) + abs(ry - cy)
            opp_d = abs(rx - ox) + abs(ry - oy)
            sc = (opp_d - self_d) * 1000 - self_d
            if sc > best:
                best = sc
        return best

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx, dy = step_towards(tx, ty, sx, sy)
        nx, ny = sx + dx, sy + dy
        return [dx, dy] if valid(nx, ny) else [0, 0]

    cand = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    best_move = [0, 0]
    best_val = -10**18
    center = ((w - 1) / 2.0, (h - 1) / 2.0)

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        val = cell_score(nx, ny)
        # tie-break: prefer being closer to any resource and to center
        tie_r = 0
        near = 10**9
        for rx, ry in resources:
            d = abs(rx - nx) + abs(ry - ny)
            if d < near:
                near = d
        tie_r = -near
        tie_c = -(abs(nx - center[0]) + abs(ny - center[1]))
        val = val + tie_r * 3 + tie_c * 0.1
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move
def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (not inb(x, y)) or ((x, y) in obstacles)
    def md(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not moves:
        return [0, 0]

    if not resources:
        best = (10**9, 10**9, 0, 0, 0)
        bx = by = 0
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if blocked(nx, ny): 
                continue
            sd = md(nx, ny, sx, sy)
            od = md(nx, ny, ox, oy)
            key = (-od, sd, dx, dy, nx)
            if key < best:
                best = key
                bx, by = dx, dy
        return [bx, by]

    best_move = [0, 0]
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue

        # Resource-competition targeting: maximize how much closer we are than the opponent.
        best_margin = -10**18
        best_res_dist = 10**18
        best_res_id = (10**18, 10**18)

        for rx, ry in resources:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            margin = od - sd  # positive means we are closer than opponent
            if (margin > best_margin) or (margin == best_margin and (sd < best_res_dist or (sd == best_res_dist and (rx, ry) < best_res_id))):
                best_margin = margin
                best_res_dist = sd
                best_res_id = (rx, ry)

        # Prefer moves that secure a winning margin; if none, go to the most contestable resource.
        # Secondary: reduce distance to that chosen resource; Tertiary: keep away from opponent.
        opp_to_best = md(ox, oy, best_res_id[0], best_res_id[1])
        key = (-best_margin, best_res_dist, -opp_to_best, nx, ny, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]
def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not res:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        best_t = res[0]
        best_val = 10**18
        for x, y in res:
            d_me = cheb(sx, sy, x, y)
            d_op = cheb(ox, oy, x, y)
            # Prefer resources I can reach earlier; otherwise reduce attractiveness.
            val = d_me * 10 - d_op * 6
            if val < best_val:
                best_val = val
                best_t = (x, y)
        tx, ty = best_t

    best_move = (0, 0)
    best_score = 10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0

        d_to = cheb(nx, ny, tx, ty)
        d_op = cheb(nx, ny, ox, oy)

        # Subtle obstacle pressure: avoid stepping adjacent to obstacles.
        adj_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                xx, yy = nx + ax, ny + ay
                if (xx, yy) in obs:
                    adj_obs += 1

        # Aim: get closer to target, keep distance from opponent, avoid obstacle congestion.
        score = d_to * 10 - d_op * 2 + adj_obs * 3

        # Deterministic tie-break: prefer staying still if equal, else smallest dx, then dy.
        if score < best_score or (score == best_score and ((dx, dy) == (0, 0) or (dx, dy) < best_move)):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            t = (int(p[0]), int(p[1]))
            if t not in obs:
                res.append(t)
    if not res:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Prefer moves that secure a contested resource soon.
        # advantage = opp_dist - my_dist (higher => we arrive first)
        # Also add a center-line bias to handle row sweeps deterministically.
        best_adv = -10**9
        score = 0
        for rx, ry in res:
            myd = cheb(nx, ny, rx, ry)
            oppd = cheb(ox, oy, rx, ry)
            adv = oppd - myd
            if adv > best_adv:
                best_adv = adv
            if myd == 0:
                score += 1000
            else:
                if adv > 0:
                    score += adv * 10 - myd
                else:
                    score += adv - myd

        # Bias: move to reduce distance to midpoint row/col between agents.
        mx = (sx + ox) // 2
        my = (sy + oy) // 2
        center_bias = - (cheb(nx, ny, mx, my))

        key = (best_adv, score + center_bias, -cheb(nx, ny, ox, oy), -cheb(nx, ny, mx, my))
        if best is None or key > best[0]:
            best = (key, [dx, dy])

    if best is None:
        return [0, 0]
    return best[1]
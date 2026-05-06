def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            blocked.add((p[0], p[1]))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            legal.append((dx, dy))

    if not legal:
        return [0, 0]

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            res.append((r[0], r[1]))

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    def adj_block_pen(nx, ny):
        cnt = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                x, y = nx + ax, ny + ay
                if (x, y) in blocked:
                    cnt += 1
        return cnt

    if not res:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        bestv = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            d = md(nx, ny, cx, cy)
            v = (d, adj_block_pen(nx, ny))
            if bestv is None or v < bestv:
                bestv, best = v, (dx, dy)
        return [best[0], best[1]] if best else [0, 0]

    dres_opp_any = min(md(ox, oy, rx, ry) for rx, ry in res)
    best = legal[0]
    best_score = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        dself = 10**9
        target = res[0]
        for rx, ry in res:
            d = md(nx, ny, rx, ry)
            if d < dself:
                dself, target = d, (rx, ry)
        trx, try_ = target
        dop_to_target = md(ox, oy, trx, try_)
        advantage = dres_opp_any - dself
        threat_gap = dop_to_target - dself
        score = 5 * threat_gap + 2 * advantage - dself - 0.8 * adj_block_pen(nx, ny)
        if score > best_score:
            best_score = score
            best = (dx, dy)
    return [best[0], best[1]]
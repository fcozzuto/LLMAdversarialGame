def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in resources:
        if r and len(r) >= 2:
            x, y = r[0], r[1]
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    dirs.sort(key=lambda d: (d[0], d[1]))  # deterministic tie order

    if not res:
        # fallback: move toward center while staying away from obstacles
        tx, ty = (w // 2, h // 2)
        best = (0, 0)
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obs:
                continue
            v = -cheb(nx, ny, tx, ty) - 0.1 * cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Evaluate each move by resource control: prefer states where we are closer than opponent
    oppd = {}
    for r in res:
        oppd[r] = cheb(ox, oy, r[0], r[1])

    best = (0, 0)
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue

        d_self_sum = 0
        d_opp_sum = 0
        win_count = 0
        nearest = 10**9
        for r in res:
            sd = cheb(nx, ny, r[0], r[1])
            od = oppd[r]
            if sd < nearest:
                nearest = sd
            if sd < od:
                win_count += 1
                d_self_sum += sd
            else:
                d_opp_sum += od

        # Strongly prefer capturing (being closer), then minimize our nearest distance
        v = 20 * win_count - 2.0 * d_self_sum - 0.3 * d_opp_sum - 1.5 * nearest - 0.05 * cheb(nx, ny, ox, oy)

        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]
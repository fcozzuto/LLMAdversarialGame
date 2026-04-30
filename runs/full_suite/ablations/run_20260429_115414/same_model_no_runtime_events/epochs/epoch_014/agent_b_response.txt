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
    dirs.sort(key=lambda d: (d[0], d[1]))

    best = (0, 0)
    bestv = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue

        if res:
            # Contention heuristic: prefer resources where we become closer than the opponent.
            # Evaluate best contest advantage this move can create.
            my_best = -10**18
            for rx, ry in res:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                # Smaller ds is good, larger do is good. Tie-break prefers also being near center slightly.
                center = cheb(nx, ny, w // 2, h // 2)
                v = (do - ds) * 10 - ds - center * 0.1
                if v > my_best:
                    my_best = v
            # Secondary: avoid walking into the opponent too closely.
            d_opp = cheb(nx, ny, ox, oy)
            score = my_best + d_opp * 0.05
        else:
            # No resources: drift toward center while staying away from opponent and obstacles.
            score = -cheb(nx, ny, w // 2, h // 2) + cheb(nx, ny, ox, oy) * 0.1

        if score > bestv:
            bestv = score
            best = (dx, dy)

    return [best[0], best[1]]
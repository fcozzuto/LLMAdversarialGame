def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def man(a, b, c, d):
        x = a - c
        if x < 0: x = -x
        y = b - d
        if y < 0: y = -y
        return x + y

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if valid(x, y):
                res.append((x, y))

    if not res:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = man(nx, ny, tx, ty)
            if best is None or d < best[0]:
                best = (d, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    # Opponent-greedy prediction: pick their nearest resource (from current position)
    opp_target = None
    opp_best_d = None
    for rx, ry in res:
        d = man(ox, oy, rx, ry)
        if opp_best_d is None or d < opp_best_d:
            opp_best_d = d
            opp_target = (rx, ry)

    tx, ty = opp_target

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_self_target = man(nx, ny, tx, ty)
        # Contention: prefer moves that close the gap to the opponent's likely target
        margin = (opp_best_d - d_self_target)
        # Also keep options open: prefer reducing distance to next-best resources if we can't beat target
        dists = []
        for rx, ry in res:
            dists.append(man(nx, ny, rx, ry))
        dists.sort()
        alt = dists[1] if len(dists) > 1 else dists[0]
        # Small tie-breakers to encourage progress (and avoid dithering)
        prog = -dists[0]
        key = (-margin, alt, -prog, dx, dy)
        if best is None or key < best[0]:
            best = (key, dx, dy)

    return [best[1], best[2]] if best else [0, 0]
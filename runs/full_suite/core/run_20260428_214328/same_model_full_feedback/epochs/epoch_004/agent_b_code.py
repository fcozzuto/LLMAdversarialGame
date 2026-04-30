def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            res.append((int(p[0]), int(p[1])))

    obs = set()
    obs_list = []
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            a = (int(p[0]), int(p[1]))
            obs.add(a)
            obs_list.append(a)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def obs_penalty(x, y):
        if (x, y) in obs:
            return 10**9
        if not obs_list:
            return 0
        md = 10**9
        for ax, ay in obs_list:
            d = abs(x - ax) + abs(y - ay)
            if d < md:
                md = d
        if md >= 4:
            return 0
        return (4 - md) * 12 + (1 if md == 0 else 0)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    opp_pos = (ox, oy)

    best = None
    best_val = -10**30

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        total = -obs_penalty(nx, ny)

        # Relative resource advantage: prefer resources closer to us than opponent.
        for rx, ry in res:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(opp_pos[0], opp_pos[1], rx, ry)
            # Positive when we are closer; also lightly prefer absolute closeness.
            total += (do - ds) * 9 - ds * 1.5

        # If resources are scarce/unseen, still bias toward the nearest available one.
        if not res:
            total = -cheb(nx, ny, opp_pos[0], opp_pos[1]) - obs_penalty(nx, ny)

        # Deterministic tie-break by fixed dir order and current best comparisons.
        if total > best_val:
            best_val = total
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]
def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best_move = [0, 0]
    best_sc = None
    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # Prefer moves that secure a resource sooner than opponent.
        best_adv = -10**9
        best_self_d = 10**9
        for rx, ry in res:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd  # positive means we get there first
            if adv > best_adv or (adv == best_adv and sd < best_self_d):
                best_adv = adv
                best_self_d = sd

        # Small tie-break: keep moving toward high-opportunity center-ish and away from opponent distance spikes.
        center_bias = -abs(nx - cx) - abs(ny - cy)
        opp_closer = cheb(ox, oy, sx, sy)
        self_closer = cheb(nx, ny, sx, sy)
        sc = (best_adv, -best_self_d, center_bias, -(opp_closer - self_closer))

        if best_sc is None or sc > best_sc:
            best_sc = sc
            best_move = [dx, dy]

    return best_move
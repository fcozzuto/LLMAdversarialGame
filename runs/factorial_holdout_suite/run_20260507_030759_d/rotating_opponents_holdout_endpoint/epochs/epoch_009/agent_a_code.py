def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    if not w or not h:
        return [0, 0]
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]
    if not resources:
        resources = [(ox, oy)]
    # Prefer actions that maximize immediate distance lead over opponent; discourage stepping next to obstacles.
    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    for dx, dy, nx, ny in candidates:
        best_adv = -10**18
        best_self = 10**18
        for rx, ry in resources:
            if not inb(rx, ry):
                continue
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            adv = od - sd
            if adv > best_adv or (adv == best_adv and sd < best_self):
                best_adv = adv
                best_self = sd

        # Obstacle proximity penalty: prefer safer cells
        adj_obs = 0
        for ax, ay in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            tx, ty = nx + ax, ny + ay
            if (tx, ty) in obs:
                adj_obs += 1

        # Tie-break: also consider moving toward the single nearest resource (with opponent threat)
        if resources:
            min_sd = 10**18
            min_threat = 10**18
            for rx, ry in resources:
                if not inb(rx, ry):
                    continue
                sd0 = dist(nx, ny, rx, ry)
                td = dist(ox, oy, rx, ry)
                if sd0 < min_sd or (sd0 == min_sd and td < min_threat):
                    min_sd = sd0
                    min_threat = td
        else:
            min_sd = 0
            min_threat = 0

        key = (best_adv, -min_sd, -min_threat, -adj_obs, dx, dy)
        if best is None or key > best[0]:
            best = (key, [dx, dy])

    return best[1]
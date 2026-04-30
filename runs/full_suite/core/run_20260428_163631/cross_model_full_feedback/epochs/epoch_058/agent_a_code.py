def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def dist(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])
    me = (sx, sy); opp = (ox, oy)
    if resources:
        best_r = None
        best_den = -10**9
        for r in resources:
            d_me = dist(me, r)
            d_opp = dist(opp, r)
            denom = d_opp - d_me  # deny when we're closer than opponent
            # slight preference for resources that are nearer overall
            denom += 0.01 * (w + h - d_me)
            if denom > best_den:
                best_den = denom
                best_r = r

        tx, ty = best_r
        # Move that best improves distance to target; if ambiguous, maximize separation from opponent.
        best = None
        best_val = -10**18
        for dx, dy, nx, ny in legal:
            nd_me = dist((nx, ny), (tx, ty))
            nd_opp = dist((nx, ny), opp)
            # also avoid stepping onto cells adjacent to obstacles too often (tight corridors)
            adj_obs = 0
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if ax == 0 and ay == 0: 
                        continue
                    px, py = nx + ax, ny + ay
                    if (px, py) in obstacles:
                        adj_obs += 1
            val = -nd_me + 0.6 * nd_opp - 0.05 * adj_obs
            if val > best_val:
                best_val = val
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    # No resources: deterministic safe-ish control toward center while increasing distance from opponent.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    best_val = -10**18
    for dx, dy, nx, ny in legal:
        to_center = abs(nx - cx) + abs(ny - cy)
        sep = dist((nx, ny), opp)
        val = -to_center + 0.8 * sep
        if val > best_val:
            best_val = val
            best = (dx, dy)
    return [int(best[0]), int(best[1])]
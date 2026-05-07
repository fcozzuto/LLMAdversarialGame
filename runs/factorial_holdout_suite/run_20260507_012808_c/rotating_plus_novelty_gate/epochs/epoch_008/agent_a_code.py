def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set(map(tuple, obstacles))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    def neighbors(x, y):
        out = []
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                out.append((dx, dy, nx, ny))
        return out if out else [(0, 0, x, y)]

    # Threats: resources where opponent is already closer or can arrive with similar advantage.
    best_r = None; best_score = None
    for rx, ry in resources:
        do = cheb(ox, oy, rx, ry)
        ds = cheb(sx, sy, rx, ry)
        # Higher is more urgent: being ahead makes it very urgent.
        urgency = (do - ds)
        # Also bias by being nearer overall.
        urgency = urgency * 2 + do
        if best_score is None or urgency < best_score:
            best_score = urgency; best_r = (rx, ry)
    tx, ty = best_r

    # Intercept: choose a target cell near the threatened resource that minimizes our distance,
    # but avoids getting stuck behind obstacles via a shallow greedy avoidance.
    candidates = []
    for dx, dy, nx, ny in neighbors(tx, ty):
        ds = cheb(sx, sy, nx, ny)
        do = cheb(ox, oy, nx, ny)
        candidates.append((ds - do, ds, dx, dy))
    # Deterministic pick: smallest (ds-do), then smallest ds.
    candidates.sort(key=lambda t: (t[0], t[1], t[2], t[3]))
    _, _, idvx, idvy = candidates[0]

    # One-step move selection with simple objective:
    # - if we can reach threatened cell now, do it
    # - otherwise, move towards the chosen intercept direction
    # - if no good, move towards nearest resource.
    sx2, sy2 = sx, sy
    if (sx, sy) == (tx, ty):
        # If already on resource, stay (engine should collect automatically).
        return [0, 0]

    # If we can move directly to threatened resource in one step, prefer it.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) == (tx, ty) and (nx, ny) not in obs:
            return [dx, dy]

    nearest = min(resources, key=lambda r: (cheb(sx, sy, r[0], r[1]), r[0], r[1]))
    nxr, nyr = nearest

    best = None
    for dx, dy, nx, ny in neighbors(sx, sy):
        # Primary: approach threatened intercept (tx,ty neighborhood) using our chosen neighbor direction.
        toward_threat = cheb(nx, ny, tx, ty)
        toward_near = cheb(nx, ny, nxr, nyr)
        # Reward moving in the intercept direction slightly.
        dir_reward = 0 if (dx == idvx and dy == idvy) else 1
        # Strongly discourage increasing distance to threat.
        score = toward_threat * 3 + toward_near + dir_reward
        if best is None or score < best[0]:
            best = (score, dx, dy)
    return [best[1], best[2]]
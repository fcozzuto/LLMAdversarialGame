def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = set((int(p[0]), int(p[1])) for p in obstacles)
    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def mind_obs_dist(x, y):
        if not obs_set:
            return 10
        m = 10**9
        for (px, py) in obs_set:
            d = cheb(x, y, px, py)
            if d < m:
                m = d
        return m

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Target selection: (1) race where we are already ahead; (2) otherwise contest where opponent is closest.
    best_r = None
    best_key = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not inb(rx, ry) or (rx, ry) in obs_set:
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        lead = od - sd
        # If we're not ahead, still pick a resource that maximizes "contest strength" (small sd and very small od).
        key = (lead > 0, lead, -(sd + 2), -od, -(rx * 8 + ry))
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    # Fallback: if no resources, move to maximize obstacle clearance.
    if best_r is None:
        cur_obsd = mind_obs_dist(sx, sy)
        best_move = (0, 0)
        best_mk = (-10**9, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs_set:
                continue
            mk = (mind_obs_dist(nx, ny), -cheb(nx, ny, ox, oy))
            if mk > best_mk:
                best_mk = mk
                best_move = (dx, dy)
        dx, dy = best_move
        return [int(dx), int(dy)]

    tx, ty = best_r
    # One-step lookahead toward target, with obstacle-clearance and a small "deny" term against opponent's reach.
    best_move = (0, 0)
    best_score = -10**18
    cur_d = cheb(sx, sy, tx, ty)
    opp_d = cheb(ox, oy, tx, ty)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny
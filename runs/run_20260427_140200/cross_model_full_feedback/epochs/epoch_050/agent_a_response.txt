def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    me = observation.get("self_position", [0, 0]) or [0, 0]
    opp = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    center = ((w - 1) / 2.0, (h - 1) / 2.0)

    # Choose a target that we are likely to beat (maximize lead), with tie-break on being far from opponent.
    best_t = resources[0]
    best_lead = None
    for t in resources:
        myd = cheb((sx, sy), t)
        opd = cheb((ox, oy), t)
        lead = opd - myd  # positive means we are closer or equal
        if best_lead is None or lead > best_lead or (lead == best_lead and opd > cheb((ox, oy), best_t)):
            best_lead = lead
            best_t = t

    # Move to improve lead to best_t; if no improvement possible, avoid making it worse; keep deterministic tie-breaks.
    tx, ty = best_t
    best_move = (0, 0)
    best_val = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        myd = cheb((nx, ny), best_t)
        opd = cheb((ox, oy), best_t)
        val = (opd - myd) * 1000  # primary: maximize lead
        # Secondary: progress toward target, discourage stepping into "tight" positions near obstacles.
        dist = myd
        val -= dist
        adj_obs = 0
        for ax, ay in dirs:
            px, py = nx + ax, ny + ay
            if (px, py) in obstacles:
                adj_obs += 1
        val -= adj_obs * 0.5
        # Tertiary: prefer moves closer to board center (helps endgame stability).
        cx, cy = center
        val -= (abs(nx - cx) + abs(ny - cy)) * 0.01
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
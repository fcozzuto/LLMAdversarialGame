def choose_move(observation):
    w = int(observation.get("grid_width", 8)); h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = set()
    for p in obstacles:
        if p is None or len(p) < 2: 
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obs_set.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dy = y1 - y2
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    def legal(x, y): return inb(x, y) and (x, y) not in obs_set

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    # If no resources, drift to safer central-ish location while staying away from opponent.
    if not resources:
        cx, cy = w // 2, h // 2
        best = (0, 0); bestv = 10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): 
                continue
            v = cheb(nx, ny, cx, cy) + 0.8 * cheb(nx, ny, ox, oy)
            if v < bestv:
                bestv = v; best = (dx, dy)
        return [best[0], best[1]]

    def obs_pen(x, y):
        if not obs_set: 
            return 0.0
        md = 10**9
        for px, py in obs_set:
            d = cheb(x, y, px, py)
            if d < md: md = d
        return 0.0 if md >= 3 else (6 - md) * 2.0

    # Pick a target resource we can plausibly win (greedy race, obstacle-aware).
    best_r = None
    best_score = 10**18
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not inb(rx, ry) or (rx, ry) in obs_set:
            continue
        d_me = cheb(sx, sy, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        # Prefer closer resources, but strongly avoid ones opponent is much closer to.
        # Also avoid resources surrounded by obstacles.
        score = d_me - 2.5 * (d_me - d_op) + obs_pen(rx, ry) + 0.15 * cheb(rx, ry, w-1-sx, h-1-sy)
        if score < best_score:
            best_score = score; best_r = (rx, ry)

    # If opponent is clearly closer to our best target, switch to a "blocking" step:
    # move toward a cell that increases our distance from opponent while reducing their progress direction.
    rx, ry = best_r
    d_me0 = cheb(sx, sy, rx, ry)
    d_op0 = cheb(ox, oy, rx, ry)
    want_block = d_op0 + 1 < d_me0

    tx, ty = (rx, ry)
    if want_block:
        # Choose a point near the line between opponent and target: midpoint-like rounded.
        mx = (ox + rx) // 2
        my = (oy + ry) // 2
        # Keep it legal and closer to our current position than raw midpoint would be.
        tx, ty = mx, my
        if (tx, ty) in obs_set or not inb(tx, ty):
            # fallback: move one step from opponent toward target, then take the cell as block.
            stepx = 0 if ox == rx else (1 if rx > ox else -1)
            stepy =
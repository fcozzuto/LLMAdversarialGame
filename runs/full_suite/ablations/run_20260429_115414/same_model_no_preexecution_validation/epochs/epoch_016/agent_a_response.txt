def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs_set = set()
    for p in obstacles:
        if p is None or len(p) < 2:
            continue
        px, py = int(p[0]), int(p[1])
        if 0 <= px < w and 0 <= py < h:
            obs_set.add((px, py))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return inb(x, y) and (x, y) not in obs_set

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def obs_near_pen(x, y):
        if not obs_set:
            return 0
        m = 10**9
        for (px, py) in obs_set:
            d = cheb(x, y, px, py)
            if d < m:
                m = d
        if m >= 3:
            return 0
        return -(4 - m) * 1.5  # mildly avoid being too close to obstacles

    # Choose targets with an obstacle-aware race metric: prefer where we are close AND opponent is far.
    scored = []
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not legal(rx, ry):
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        if od <= sd and sd > 0:
            # If opponent is not behind, we only consider it if we can still reduce their lead soon.
            gain = od - sd
        else:
            gain = od - sd
        finish = 12 - sd  # higher when closer
        scored.append((-(gain * 2 + finish) , gain, finish, rx, ry))
    scored.sort()
    if scored:
        # Take up to 3 best candidates deterministically.
        cand = []
        for item in scored[:3]:
            cand.append((item[3], item[4]))
    else:
        cand = [(ox, oy), (sx, sy)]

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        opp_d = cheb(ox, oy, nx, ny)
        avoid = -opp_d * 0.2  # slight pressure to avoid being immediately adjacent
        progress = 0
        lead_after = -10**9
        for (rx, ry) in cand:
            sd2 = cheb(nx, ny, rx, ry)
            od2 = cheb(ox, oy, rx, ry)
            lead = od2 - sd2  # larger means we are closer than opponent (or opponent farther)
            fin = 10 - sd2
            near_obs = obs_near_pen(nx, ny)
            val = lead * 3.0 + fin * 1.2 + near_obs
            if val > progress:
                progress = val
            if lead > lead_after:
                lead_after = lead
        # Strongly favor moves that increase lead against at least one candidate resource.
        total = progress + avoid + (lead_after * 0.6)
        if total > best_val:
            best_val = total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
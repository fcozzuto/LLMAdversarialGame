def choose_move(observation):
    w = int(observation.get("grid_width", 8)); h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs_set = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def legal(x, y): return inb(x, y) and (x, y) not in obs_set
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    def obs_pen(x, y):
        if not obs_set: return 0.0
        md = 99
        for px, py in obs_set:
            d = cheb(x, y, px, py)
            if d < md: md = d
            if md == 0: break
        if md <= 1: return 3.0
        if md == 2: return 1.2
        return 0.0

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    # If no resources, drift to center while maximizing distance advantage.
    if not resources:
        cx, cy = w // 2, h // 2
        best_s, best_d = -10e9, (0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): 
                continue
            s = (cheb(ox, oy, nx, ny) - cheb(ox, oy, sx, sy)) + (-(cheb(nx, ny, cx, cy)))
            s -= 0.6 * obs_pen(nx, ny)
            if s > best_s:
                best_s, best_d = s, (dx, dy)
        return [int(best_d[0]), int(best_d[1])]

    best_s, best_d = -10e9, (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # Maximize being closer to some resource than opponent and keep moving toward it.
        s = 0.0
        s -= 0.7 * obs_pen(nx, ny)
        # Prefer moves that reduce distance to closest resource.
        d_self_min = 99
        d_opp_min = 99
        for rx, ry in resources:
            rx = int(rx); ry = int(ry)
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)  # opponent target distance estimate
            if ds < d_self_min: d_self_min = ds
            if do < d_opp_min: d_opp_min = do
            # Reward winning the race for each resource (scaled).
            # If we can reach much sooner than opponent, prioritize strongly.
            s += (do - ds) * 1.6 / (1 + ds)
        # Also keep overall distance from opponent growing.
        s += (cheb(ox, oy, nx, ny) - cheb(ox, oy, sx, sy)) * 0.9
        # Mild pull toward resources overall.
        s += -0.4 * d_self_min + 0.15 * (d_opp_min - d_self_min)
        if s > best_s:
            best_s, best_d = s, (dx, dy)

    return [int(best_d[0]), int(best_d[1])]
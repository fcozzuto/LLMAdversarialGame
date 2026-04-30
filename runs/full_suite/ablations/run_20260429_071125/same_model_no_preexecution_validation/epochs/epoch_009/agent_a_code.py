def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    rem = observation.get("remaining_resource_count", len(resources) if resources else 0)
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid_cell(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(a, b, c, d): 
        dx = a-c if a>=c else c-a
        dy = b-d if b>=d else d-b
        return dx if dx >= dy else dy
    def obs_pen(x, y):
        p = 0
        for dx in (-1,0,1):
            for dy in (-1,0,1):
                if dx==0 and dy==0: 
                    continue
                nx, ny = x+dx, y+dy
                if inb(nx, ny) and (nx, ny) in obstacles:
                    p += 1
        return p

    # If we have no resources, drift away from opponent while keeping away from obstacles
    if not resources or rem <= 0:
        best = (-10**18, 0, 0)
        for dx, dy in moves:
            nx, ny = sx+dx, sy+dy
            if not inb(nx, ny): 
                continue
            if (nx, ny) in obstacles:
                continue
            d_opp = cheb(nx, ny, ox, oy)
            score = d_opp*10 - obs_pen(nx, ny)*2
            if score > best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]

    # Pick move that maximizes "resource lead" using obstacle-agnostic distance + obstacle avoidance
    best = (-10**18, 0, 0)
    alpha = 0.6 + (rem/12.0)*0.3  # more aggressive when more resources remain
    beta = 0.9
    cx0, cy0 = (w-1)/2.0, (h-1)/2.0

    for dx, dy in moves:
        nx, ny = sx+dx, sy+dy
        if not valid_cell(nx, ny):
            continue

        # Evaluate best resource for this candidate
        cur_best_gap = -10**18
        cur_best_dist = 10**9
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            gap = do - ds  # positive if we are closer than opponent
            if gap > cur_best_gap or (gap == cur_best_gap and ds < cur_best_dist):
                cur_best_gap = gap
                cur_best_dist = ds

        # Center/anti-stagnation + obstacle proximity penalty
        dist_center = cheb(nx, ny, int(cx0), int(cy0))
        score = (cur_best_gap*12) - (cur_best_dist*alpha) - (obs_pen(nx, ny)*beta) - dist_center*0.2
        # Also slightly prefer moves that increase distance from opponent overall
        score += (cheb(nx, ny, ox, oy) - cheb(sx, sy, ox, oy))*1.0

        if score > best[0]:
            best = (score, dx, dy)

    return [best[1], best[2]]
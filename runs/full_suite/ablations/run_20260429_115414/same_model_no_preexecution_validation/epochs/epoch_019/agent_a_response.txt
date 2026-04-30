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

    def inb(x, y): 
        return 0 <= x < w and 0 <= y < h
    def legal(x, y): 
        return inb(x, y) and (x, y) not in obs_set

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    def obs_pen(x, y):
        if not obs_set: 
            return 0
        m = 99
        for px, py in obs_set:
            d = cheb(x, y, px, py)
            if d < m: 
                m = d
        if m <= 1: 
            return 2.5
        if m == 2: 
            return 1.2
        return 0.0

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best = (None, -10e9)

    # If no resources, maximize staying away while moving toward center a bit.
    if not resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): 
                continue
            score = 0.9 * cheb(nx, ny, ox, oy) - 0.15 * cheb(nx, ny, int(cx), int(cy)) - 0.5 * obs_pen(nx, ny)
            if score > best[1]:
                best = ((dx, dy), score)
        if best[0] is None: 
            return [0, 0]
        return [best[0][0], best[0][1]]

    # Resource targeting: prioritize states where we reduce opponent lead toward a specific resource.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny): 
            continue

        move_score = -0.8 * cheb(nx, ny, ox, oy) * 0.0  # keep deterministic shape; no-op on opponent distance directly
        local_best = -10e9

        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            dm = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Positive when we are closer than opponent.
            lead = do - dm
            # Encourage quick capture and avoid positions that let opponent be much closer.
            # Also slightly bias toward resources not too far from our current area.
            cap = 2.8 * lead - 1.05 * dm - 0.15 * cheb(rx, ry, sx, sy)
            # If opponent is already on/adjacent to the resource, defend by weighting lead more.
            if do <= 1:
                cap += 3.0 * lead - 0.6 * dm
            cap -= 0.35 * obs_pen(nx, ny)
            if cap > local_best:
                local_best = cap

        # Small preference to not oscillate: prefer reducing distance to the best resource target next.
        # Deterministic: approximate by subtracting distance to closest resource from next position.
        dmin = 99
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            d = cheb(nx, ny, rx, ry)
            if d < dmin: 
                dmin = d
        local_best -= 0.08 * dmin
        move_score = local_best

        if move_score > best[1]:
            best = ((dx, dy), move_score)

    if best[0] is
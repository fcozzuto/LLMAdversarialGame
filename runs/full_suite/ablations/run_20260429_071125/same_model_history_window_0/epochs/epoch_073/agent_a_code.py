def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    candidates = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x,y): return 0 <= x < w and 0 <= y < h
    def md(a,b,c,d): 
        dx = a-c; 
        if dx < 0: dx = -dx
        dy = b-d
        if dy < 0: dy = -dy
        return dx + dy
    # If no resources, just run away deterministically.
    if not resources:
        bx = -1; by = -1; best = None
        for dx, dy in candidates:
            nx, ny = sx+dx, sy+dy
            if not inb(nx,ny) or (nx,ny) in obstacles: 
                continue
            d = md(nx,ny,ox,oy)
            val = d
            if best is None or val > best:
                best = val; bx = dx; by = dy
        if best is None: return [0,0]
        return [bx, by]
    best_dx, best_dy, best_val = 0, 0, -10**9
    for dx, dy in candidates:
        nx, ny = sx+dx, sy+dy
        if not inb(nx,ny) or (nx,ny) in obstacles:
            continue
        # Prefer stepping onto a resource.
        on_resource = 1 if (nx,ny) in set((r[0],r[1]) for r in resources) else 0
        # Evaluate best available resource from this candidate.
        best_resource_score = -10**9
        for r in resources:
            rx, ry = r[0], r[1]
            myd = md(nx,ny,rx,ry)
            opd = md(ox,oy,rx,ry)
            # Our advantage on this resource; also bias toward closer resources.
            adv = opd - myd
            # Slight penalty if opponent could immediately take while we move away.
            take_risk = 0
            if opd <= myd: take_risk = 1
            # Combine: strong preference for advantage, then proximity.
            score = adv * 10 - myd - take_risk * 3
            if score > best_resource_score:
                best_resource_score = score
        # Keep some distance from opponent unless we can grab a resource.
        opp_dist = md(nx,ny,ox,oy)
        opp_pen = 0
        if opp_dist <= 2: opp_pen = (3 - opp_dist) * 2
        # Obstacle avoidance already via filtering; add tie-breaker toward staying in bounds center-ish.
        center_bias = -abs((nx - (w-1)/2)) - abs((ny - (h-1)/2))
        val = best_resource_score + on_resource * 50 + opp_dist * 0.2 - opp_pen + center_bias * 0.05
        if val > best_val:
            best_val = val; best_dx, best_dy = dx, dy
    # If all candidate moves were invalid, stay.
    return [int(best_dx), int(best_dy)]
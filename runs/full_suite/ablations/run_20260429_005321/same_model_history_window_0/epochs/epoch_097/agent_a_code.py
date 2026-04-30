def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x,y): return 0 <= x < w and 0 <= y < h
    def step_dist(x1,y1,x2,y2): dx = abs(x1-x2); dy = abs(y1-y2); return dx if dx > dy else dy
    def best_value(px,py):
        if resources:
            best = -10**9
            for rx, ry in resources:
                if (rx, ry) in obstacles: 
                    continue
                sd = step_dist(px,py,rx,ry)
                od = step_dist(ox,oy,rx,ry)
                # Prefer securing resources (od- sd large), tie-break with shorter own distance
                val = (od - sd) * 3 - sd
                # slight preference to nearer resources to reduce dithering
                val += -0.1 * (abs(px-rx)+abs(py-ry))
                if val > best: best = val
            return best
        # No resources: drift toward center, but also avoid obstacles via candidate scoring elsewhere
        cx, cy = (w-1)//2, (h-1)//2
        return -step_dist(px,py,cx,cy)
    # If resources exist but we are disadvantaged overall, shift to interception
    def overall_disadvantage():
        if not resources: return False
        best_gap = -10**9
        for rx, ry in resources:
            sd = step_dist(sx,sy,rx,ry); od = step_dist(ox,oy,rx,ry)
            best_gap = max(best_gap, od - sd)
        # If opponent is generally closer (negative or small gaps), intercept
        return best_gap < 0
    intercept = overall_disadvantage()
    best_move = (0,0); best_score = -10**9
    center_bias = -0.03 * step_dist(sx,sy,(w-1)//2,(h-1)//2)
    for dx,dy in moves:
        nx, ny = sx+dx, sy+dy
        if not inb(nx,ny) or (nx,ny) in obstacles:
            continue
        if intercept and resources:
            # Intercept: move to reduce distance to opponent while not walking into obstacles
            score = -step_dist(nx,ny,ox,oy) * 2
            score += center_bias
        else:
            score = best_value(nx,ny)
            # small bias to avoid staying when a better option exists
            if dx == 0 and dy == 0: score -= 0.2
        if score > best_score:
            best_score = score
            best_move = (dx,dy)
    return [int(best_move[0]), int(best_move[1])]
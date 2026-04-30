def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []); obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    move_opts = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def inb(x,y): return 0 <= x < w and 0 <= y < h
    def md(x1,y1,x2,y2): return abs(x1-x2)+abs(y1-y2)
    if not resources:
        best = (10**9, 0, 0)
        for dx,dy in move_opts:
            nx, ny = sx+dx, sy+dy
            if not inb(nx,ny) or (nx,ny) in obstacles: 
                continue
            v = md(nx,ny,ox,oy)  # drift away if no resources
            if v < best[0] or (v==best[0] and (dx,dy) < (best[1],best[2])):
                best = (v, dx, dy)
        return [best[1], best[2]]
    # Target resources: minimize weighted distance to resource with opponent-aware term (favor resources we can reach first)
    best = (10**18, 0, 0)
    for dx,dy in move_opts:
        nx, ny = sx+dx, sy+dy
        if not inb(nx,ny) or (nx,ny) in obstacles:
            continue
        opp_to = md(nx,ny,ox,oy)
        v = 10**18
        for rx, ry in resources:
            d_self = md(nx,ny,rx,ry)
            d_opp = md(ox,oy,rx,ry)
            # favor moves that reduce our reach time, and resources where opponent is not advantaged
            cand = (0.4 * d_self + 0.6 * d_opp) + 0.08 * opp_to
            # small obstacle proximity penalty (discourage stepping into clutter)
            if (nx-1,ny) in obstacles or (nx+1,ny) in obstacles or (nx,ny-1) in obstacles or (nx,ny+1) in obstacles:
                cand += 0.15
            if cand < v: v = cand
        # deterministic tie-break by lower dx/dy via tuple
        key = (v, dx, dy)
        if key < best: best = key
    # If all moves invalid (shouldn't happen), stay
    return [best[1], best[2]]
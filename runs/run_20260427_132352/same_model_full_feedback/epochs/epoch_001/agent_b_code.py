def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    cand = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x,y): return 0 <= x < w and 0 <= y < h
    def dist(a,b,c,d):
        dx = a-c
        dy = b-d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx + dy
    if not resources:
        cx, cy = (w-1)/2.0, (h-1)/2.0
        best = (0,0)
        bestv = -10**9
        for dx,dy in cand:
            nx, ny = sx+dx, sy+dy
            if not inb(nx,ny): continue
            v = -abs(nx-cx)-abs(ny-cy)
            if (nx,ny) in obstacles: v -= 5
            if v > bestv: bestv = v; best = [dx,dy]
        return best
    best = [0,0]
    bestv = -10**9
    for dx,dy in cand:
        nx, ny = sx+dx, sy+dy
        if not inb(nx,ny): continue
        v = 0
        if (nx,ny) in obstacles:
            v -= 1000
        else:
            # Prefer taking resources where we are closer (or at least not further)
            best_res = -10**9
            for rx, ry in resources:
                if (rx,ry) in obstacles: 
                    continue
                d_me = dist(nx,ny,rx,ry)
                d_op = dist(ox,oy,rx,ry)
                # Higher when we are closer; also favor smaller absolute distance
                rel = d_op - d_me
                score = rel * 10 - d_me
                if d_me == 0: score += 500
                best_res = score if score > best_res else best_res
            v += best_res
        # Small tie-break toward opponent pressure: avoid giving up by staying too far
        d_opp = dist(nx,ny,ox,oy)
        v += -0.1 * d_opp
        if v > bestv:
            bestv = v
            best = [dx,dy]
    return best
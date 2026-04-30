def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    cand = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x,y): return 0 <= x < w and 0 <= y < h and (x,y) not in obstacles
    def dist(a,b): 
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))  # Chebyshev for grid+diagonals
    if not resources:
        tx, ty = (w-1)//2, (h-1)//2
        best = None; bestv = None
        for dx,dy in cand:
            nx, ny = sx+dx, sy+dy
            if not inb(nx,ny): continue
            v = -dist((nx,ny),(tx,ty))
            if bestv is None or v > bestv: bestv, best = v, [dx,dy]
        return best if best is not None else [0,0]

    best = None; bestv = None
    for dx, dy in cand:
        nx, ny = sx+dx, sy+dy
        if not inb(nx,ny): continue
        best_adv = -10**9
        best_own = 10**9
        for rx, ry in resources:
            d_s = dist((nx,ny),(rx,ry))
            d_o = dist((ox,oy),(rx,ry))
            adv = d_o - d_s
            if adv > best_adv or (adv == best_adv and d_s < best_own):
                best_adv, best_own = adv, d_s
        # Prefer winning the race to a resource; slight bias toward center and staying safe from obstacles (implicitly via inb)
        cx, cy = (w-1)//2, (h-1)//2
        center_bias = -dist((nx,ny),(cx,cy)) * 0.01
        v = best_adv + center_bias - best_own * 0.001
        if bestv is None or v > bestv:
            bestv, best = v, [dx,dy]
    return best if best is not None else [0,0]
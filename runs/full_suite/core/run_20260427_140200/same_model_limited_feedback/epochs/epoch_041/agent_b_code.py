def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def inb(x,y): return 0 <= x < w and 0 <= y < h
    def dist(a,b,c,d):
        dx = a-c; dy = b-d
        return (dx*dx + dy*dy)
    opp_to_res = []
    for r in resources:
        rx, ry = r
        if (rx, ry) not in obstacles:
            opp_to_res.append((dist(ox, oy, rx, ry), rx, ry))
    if not opp_to_res:
        best = None; bestv = -10**18
        for dx,dy in dirs:
            nx, ny = sx+dx, sy+dy
            if not inb(nx,ny) or (nx,ny) in obstacles: continue
            v = -dist(nx,ny,ox,oy) + (nx+ny) * 1e-3
            if v > bestv: bestv = v; best = (dx,dy)
        if best is None: return [0,0]
        return [best[0], best[1]]
    opp_best_sorted = sorted(opp_to_res, key=lambda t: t[0])
    candidate_best = None; candidate_bestv = -10**18
    for dx,dy in dirs:
        nx, ny = sx+dx, sy+dy
        if not inb(nx,ny) or (nx,ny) in obstacles: continue
        bestv = -10**18
        d_opp_min, rbx, rby = opp_best_sorted[0]
        for d_opp, rx, ry in opp_best_sorted[:3]:
            d_self = dist(nx, ny, rx, ry)
            v = (d_opp - d_self) - 0.05*d_self - 0.001*dist(nx,ny,ox,oy)
            if (rx,ry)==(rbx,rby): v += 0.0005
            if v > bestv: bestv = v
        if bestv > candidate_bestv:
            candidate_bestv = bestv
            candidate_best = (dx,dy)
    if candidate_best is None: return [0,0]
    return [int(candidate_best[0]), int(candidate_best[1])]
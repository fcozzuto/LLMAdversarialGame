def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    me = observation["self_position"]
    op = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    cx, cy = me[0], me[1]
    ox, oy = op[0], op[1]
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x,y): return 0 <= x < w and 0 <= y < h
    def dist(a,b,c,d):  # Chebyshev for grid with diagonals
        dx = abs(a-c); dy = abs(b-d)
        return dx if dx > dy else dy
    if not resources:
        # drift toward opponent’s side slightly to reduce their mobility
        tx = (ox + (w//2))//2
        ty = (oy + (h//2))//2
        best = [0,0,10**9,10**9,None]
        for dx,dy in moves:
            nx, ny = cx+dx, cy+dy
            if not inb(nx,ny) or (nx,ny) in obstacles: continue
            sc = dist(nx,ny,tx,ty)
            if sc < best[2] or (sc == best[2] and (dx,dy) < (best[0],best[1])):
                best = [dx,dy,sc,0,(nx,ny)]
        if best[0] is None:
            return [0,0]
        return [best[0], best[1]]
    best = None
    for dx,dy in moves:
        nx, ny = cx+dx, cy+dy
        if not inb(nx,ny) or (nx,ny) in obstacles:
            continue
        # Prefer resources that are closer to us and relatively farther from the opponent
        best_val = None
        for rx, ry in resources:
            dme = dist(nx,ny,rx,ry)
            dop = dist(ox,oy,rx,ry)
            # Lower is better: we want to be closer than opponent
            val = dme - 0.55*dop + (0.02*(rx-3.5)**2 + 0.02*(ry-3.5)**2)
            if best_val is None or val < best_val:
                best_val = val
        # If standing on a resource, prioritize heavily (likely collection)
        on_res = (nx,ny) in set(tuple(p) for p in resources)
        score = (0 if on_res else 1, best_val, dist(nx,ny,resources[0][0],resources[0][1]))
        if best is None or score < best[0] or (score == best[0] and (dx,dy) < best[1]):
            best = [score, (dx,dy)]
    if best is None:
        return [0,0]
    return [best[1][0], best[1][1]]
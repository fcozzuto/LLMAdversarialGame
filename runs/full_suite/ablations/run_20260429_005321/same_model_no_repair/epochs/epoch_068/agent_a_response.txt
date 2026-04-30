def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obst_pen(x, y):
        if not inb(x, y): return 10**6
        p = 0
        if (x, y) in obst: p += 100000
        for nx, ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
            if (nx, ny) in obst: p += 20
        return p

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    if not resources:
        tx, ty = (w-1)//2, (h-1)//2
    else:
        best = None
        best_key = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Favor resources opponent is farther from; penalize if target is near obstacles.
            key = ((do - ds),
                   -min(ds, cheb(ox, oy, rx, ry)),
                   -obst_pen(rx, ry),
                   ds, rx, ry)
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best

    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        ds = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # Small nudge to avoid getting stuck near obstacles while closing in.
        score = ((do - ds), -ds, -obst_pen(nx, ny), -abs(nx - ox) - abs(ny - oy))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]
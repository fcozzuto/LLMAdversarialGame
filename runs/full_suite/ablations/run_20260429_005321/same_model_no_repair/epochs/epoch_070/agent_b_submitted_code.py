def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obst_adj(x, y):
        if (x, y) in obst: return 10**6
        p = 0
        for nx, ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1),(x-1,y-1),(x+1,y+1),(x-1,y+1),(x+1,y-1)):
            if (nx, ny) in obst: p += 3
        return p

    # Select global target deterministically
    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            if (rx, ry) in obst:
                continue
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            lead = do - ds  # positive means we're closer
            key = (lead, -ds, -obst_adj(rx, ry), -do, rx, ry)
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        if best is None:
            best = ((w - 1) // 2, (h - 1) // 2)
        tx, ty = best
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    # If opponent is clearly closer to the chosen target, switch to opponent's nearest resource to contest
    if resources:
        ds_t = cheb(sx, sy, tx, ty)
        do_t = cheb(ox, oy, tx, ty)
        if do_t < ds_t - 1:
            best_o = None
            best_ok = None
            for rx, ry in resources:
                if (rx, ry) in obst:
                    continue
                do = cheb(ox, oy, rx, ry)
                ds = cheb(sx, sy, rx, ry)
                key = (do, ds, abs(rx - tx) + abs(ry - ty), rx, ry)
                if best_ok is None or key < best_ok:
                    best_ok = key
                    best_o = (rx, ry)
            if best_o is not None:
                tx, ty = best_o

    # Choose move that reduces distance to target;
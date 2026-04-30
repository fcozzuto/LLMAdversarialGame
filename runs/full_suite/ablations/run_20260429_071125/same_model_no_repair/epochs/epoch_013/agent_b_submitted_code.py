def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = {(p[0], p[1]) for p in obstacles}

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2): return max(abs(x1 - x2), abs(y1 - y2))
    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    def obstacle_pen(x, y):
        p = 0
        if (x, y) in occ:
            return 10**6
        for nx, ny in [(x-1,y),(x+1,y),(x,y-1),(x,y+1),(x-1,y-1),(x+1,y-1),(x-1,y+1),(x+1,y+1)]:
            if (nx, ny) in occ:
                p += 3 if (nx, ny) in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)] else 2
        return p

    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny): 
                continue
            if (nx, ny) in occ:
                continue
            val = -man(nx, ny, ox, oy) - obstacle_pen(nx, ny) + 0.01 * ((w-1)/2 - abs(nx-(w-1)/2) + (h-1)/2 - abs(ny-(h-1)/2))
            if best is None or val > best[0]:
                best = (val, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    resset = {(p[0], p[1]) for p in resources}
    if (sx, sy) in resset:
        stay_ok = (0, 0) not in [] and (sx, sy) in resset
        if stay_ok:
            return [0, 0]

    # Target selection: prefer resources where we're comparatively closer than opponent.
    best_res = None
    for rx, ry in resset:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        score = (opd - myd) - 0.2 * myd - 0.01 * man(rx, ry, (w-1)/2, (h-1)/2)
        if best_res is None or score > best_res[0]:
            best_res = (score, rx, ry)
    _, tx, ty = best_res

    # Move selection: maximize progress to target while accounting for opponent pressure and obstacles.
    best = None
    cur_to_t = cheb(sx, sy, tx, ty)
    my_to_opp = cheb(sx, sy, ox, oy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in occ:
            continue
        d = cheb(nx, ny, tx, ty)
        # Opponent pressure at the target: if opponent is close, we value quicker acquisition.
        opp_d = cheb(ox, oy, tx, ty)
        reach_bonus = 8 if cheb(nx, ny, tx, ty) <= 1 else (4 if cheb(nx, ny, tx, ty) == 2 else 0)
        blockish = 0
        if opp_d <= 2 and myd <= opp_d:
            # If we are in a contested situation, favor moves that reduce my distance more.
            blockish = 2 * (cur_to_t - d)
        # If opponent is adjacent, prefer moves that keep distance from opponent unless it costs too much progress.
        opp_dist_after = cheb(nx, ny, ox, oy)
        opp_term = 1.5 * (opp_dist_after - my_to_opp)
        # Small bias to avoid
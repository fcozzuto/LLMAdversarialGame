def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def clamp(a, lo, hi):
        return lo if a < lo else hi if a > hi else a
    def cheb(a,b,c,d):
        dx = a-c; dx = dx if dx >= 0 else -dx
        dy = b-d; dy = dy if dy >= 0 else -dy
        return dx if dx > dy else dy
    def inside(x,y):
        return 0 <= x < w and 0 <= y < h
    my_now = (sx, sy); opp_now = (ox, oy)
    if not resources:
        tx, ty = (w//2, h//2)
        best = None
        bestv = 10**9
        for dx, dy in moves:
            nx, ny = sx+dx, sy+dy
            if not inside(nx, ny) or (nx, ny) in obstacles: 
                continue
            v = cheb(nx, ny, tx, ty)
            if v < bestv or (v == bestv and (best is None or (dx,dy) < best)):
                bestv = v; best = (dx, dy)
        return list(best) if best is not None else [0, 0]
    best_target = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        key = (opd - myd, -myd)  # maximize lead, then smaller my distance
        if best_key is None or key > best_key or (key == best_key and (rx, ry) < best_target):
            best_key = key; best_target = (rx, ry)
    rx, ry = best_target
    best = (0, 0)
    bestv = None
    myd0 = cheb(sx, sy, rx, ry)
    opd0 = cheb(ox, oy, rx, ry)
    for dx, dy in moves:
        nx, ny = sx+dx, sy+dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        myd = cheb(nx, ny, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # evaluate: prioritize getting closer to target; also try to reduce opponent's effective lead
        # and avoid moving into immediate opponent contact
        opp_contact = 1 if cheb(nx, ny, ox, oy) <= 1 else 0
        lead_now = opd0 - myd0
        lead_after = opd - myd
        v = (myd * 10) + opp_contact * 50 + (-(lead_after - lead_now) * 2)
        if bestv is None or v < bestv or (v == bestv and (dx, dy) < best):
            bestv = v; best = (dx, dy)
    return [int(best[0]), int(best[1])]
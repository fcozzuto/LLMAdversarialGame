def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def cheb(a,b,c,d): 
        da = abs(a-c); db = abs(b-d)
        return da if da>db else db
    def inb(x,y): 
        return 0 <= x < w and 0 <= y < h
    def step_to(tx, ty):
        best = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny): 
                continue
            pen = 0
            if (nx, ny) in obstacles:
                pen = 10
            d = cheb(nx, ny, tx, ty) + pen
            if best is None or d < best[0]:
                best = (d, dx, dy)
        return [best[1], best[2]] if best else [0, 0]
    # Choose best resource by relative distance; if can't catch up, contest opponent.
    best_tx, best_ty = sx, sy
    best_val = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        val = myd - 0.6 * opd  # lower is better; favor resources opponent isn't closer to
        if best_val is None or val < best_val or (val == best_val and (rx < best_tx or (rx == best_tx and ry < best_ty))):
            best_val = val
            best_tx, best_ty = rx, ry
    myd_best = cheb(sx, sy, best_tx, best_ty)
    opd_best = cheb(ox, oy, best_tx, best_ty) if (best_tx, best_ty) != (sx, sy) else 10**9
    # Strategic switch: if opponent is significantly closer, move to contest/intercept.
    if resources and (opd_best + 1 < myd_best or best_val is None or best_val > 1.2):
        # Intercept by moving towards a cell adjacent to opponent in direction that also keeps resources viable.
        tx, ty = ox, oy
        # Bias towards reducing distance to opponent while not stepping into obstacles.
        return step_to(tx, ty)
    return step_to(best_tx, best_ty)
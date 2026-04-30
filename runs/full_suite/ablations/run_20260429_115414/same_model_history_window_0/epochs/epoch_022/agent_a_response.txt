def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    # If no resources, just keep distance/avoid obstacles: move away from opponent if possible.
    moves = [(0,0),(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
    def in_bounds(x,y):
        return 0 <= x < w and 0 <= y < h and (x,y) not in obstacles
    if not resources:
        best = (10**9, (0,0))
        for dx,dy in moves:
            nx, ny = sx+dx, sy+dy
            if not in_bounds(nx,ny): 
                continue
            d = (nx-ox)*(nx-ox) + (ny-oy)*(ny-oy)
            if d > best[0]:
                best = (d, (dx,dy))
        dx, dy = best[1]
        return [int(dx), int(dy)]

    def dist2(ax,ay,bx,by):
        dx = ax-bx
        dy = ay-by
        return dx*dx + dy*dy

    opp_to = dist2(ox,oy,sx,sy)
    best_score = -10**18
    best_move = (0,0)

    # Choose a target resource that we can reach no later than opponent if possible.
    # Deterministic: evaluate targets in sorted order.
    res_sorted = sorted(resources, key=lambda p:(p[0],p[1]))
    target = res_sorted[0]
    best_gap = -10**18
    for rx, ry in res_sorted:
        # Use Manhattan as proxy for reachability; still deterministic.
        us = abs(sx-rx)+abs(sy-ry)
        op = abs(ox-rx)+abs(oy-ry)
        gap = op - us  # positive means we're closer
        # Prefer resources we're closer to; if none, pick with smallest combined distance.
        if gap > best_gap:
            best_gap = gap
            target = (rx, ry)
        elif gap == best_gap:
            if us+op < abs(sx-target[0])+abs(sy-target[1]) + abs(ox-target[0])+abs(oy-target[1]):
                target = (rx, ry)

    tx, ty = target
    # Evaluate immediate move with obstacle avoidance; tie-break by move order.
    for dx, dy in moves:
        nx, ny = sx+dx, sy+dy
        if not in_bounds(nx, ny):
            continue
        # Base: move closer to target
        s1 = -dist2(nx, ny, tx, ty)
        # Security: don't allow opponent to be much closer to target after our move
        my_m = abs(nx-tx)+abs(ny-ty)
        op_m = abs(ox-tx)+abs(oy-ty)
        s2 = 3.0*(my_m <= op_m) + 1.5*(op_m - my_m)  # higher if we're competitive
        # Pressure: increase distance from opponent slightly to reduce blocking
        s3 = 0.01*dist2(nx, ny, ox, oy)
        # Resource capture incentive (if on resource)
        s4 = 1000000.0 if (nx,ny) == (tx,ty) else 0.0
        score = s1 + s2 + s3 + s4
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
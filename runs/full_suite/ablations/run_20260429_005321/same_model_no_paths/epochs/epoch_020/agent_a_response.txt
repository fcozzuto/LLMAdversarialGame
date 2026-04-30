def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inside(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    if any(sx == rx and sy == ry for rx, ry in resources):
        return [0, 0]

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    if not resources:
        best = (0, 0, -10**9)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            opp_d = cheb(nx, ny, ox, oy)
            free = sum(1 for ddx, ddy in deltas if valid(nx + ddx, ny + ddy))
            val = opp_d * 100 + free
            if val > best[2]:
                best = (dx, dy, val)
        return [best[0], best[1]]

    best = (0, 0, -10**18)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        free = sum(1 for ddx, ddy in deltas if valid(nx + ddx, ny + ddy))
        # Evaluate moving state against best resource
        best_target = -10**18
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            my_adv = od - sd  # positive means we are closer than opponent
            risk = cheb(nx, ny, ox, oy)  # keep some distance
            # prefer capturing sooner and increasing advantage; lightly avoid clustering with opponent
            val = my_adv * 1000 - sd * 10 + free * 2 - risk * 0.5
            if val > best_target:
                best_target = val
        if best_target > best[2]:
            best = (dx, dy, best_target)
    return [best[0], best[1]]
def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (not inb(x, y)) or ((x, y) in obs)
    def cheb(x1, y1, x2, y2): 
        dx = x1 - x2; dy = y1 - y2
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if blocked(sx, sy): 
        for dx, dy in ((0,0), (1,0), (-1,0), (0,1), (0,-1), (1,1), (1,-1), (-1,1), (-1,-1)):
            nx, ny = sx + dx, sy + dy
            if not blocked(nx, ny): 
                return [dx, dy]
        return [0, 0]

    if not resources:
        return [0, 0]

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best = None; best_score = -10**18

    # Precompute opponent preference (deterministic tie-breaker by resource order)
    res_list = [(r[0], r[1]) for r in resources]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny): 
            continue

        # Evaluate resources: prefer ones we can reach sooner, and where opponent is slower.
        # If multiple, prefer closer to our position after move, and then higher "threat gap".
        cur_best_val = -10**18
        for i, (rx, ry) in enumerate(res_list):
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Higher is better; negative myd penalizes distance; big bonus if we can arrive earlier.
            gap = opd - myd
            val = (gap * 100) - myd * 3 + (i * -1)  # i*-1 provides deterministic preference
            if val > cur_best_val:
                cur_best_val = val

        # Also add a small term to reduce chances of being blocked by opponent pathing:
        # keep farther from opponent if no resource can be won quickly.
        overall = cur_best_val + cheb(nx, ny, ox, oy) * 0.1
        if overall > best_score:
            best_score = overall
            best = [dx, dy]
        elif overall == best_score and best is not None:
            # deterministic tie-break: prefer smallest dx, then dy
            if dx < best[0] or (dx == best[0] and dy < best[1]):
                best = [dx, dy]

    return best if best is not None else [0, 0]
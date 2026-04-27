def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def cheb(a, b): 
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    def in_bounds(x, y): 
        return 0 <= x < w and 0 <= y < h
    best_move = [0, 0]
    if not resources:
        best_val = 10**9
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue
            val = cheb((nx, ny), (ox, oy))
            if val < best_val:
                best_val = val
                best_move = [dx, dy]
        return best_move
    best_val = 10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        my_pos = (nx, ny)
        opp_pos = (ox, oy)
        best_here = 10**18
        for r in resources:
            rpos = (r[0], r[1])
            ds = cheb(my_pos, rpos)
            dos = cheb(opp_pos, rpos)
            v = ds - 0.35 * dos
            if ds == 0:
                v -= 3.0
            if v < best_here:
                best_here = v
        # Mild preference to not get trapped near obstacles: count adjacent free squares
        adj_free = 0
        for adx, ady in deltas:
            tx, ty = nx + adx, ny + ady
            if in_bounds(tx, ty) and (tx, ty) not in obstacles:
                adj_free += 1
        v2 = best_here - 0.02 * adj_free
        if v2 < best_val:
            best_val = v2
            best_move = [dx, dy]
    return best_move
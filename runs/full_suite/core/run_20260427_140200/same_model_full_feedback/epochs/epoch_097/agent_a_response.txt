def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    neigh = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def obstacle_adjacency(x, y):
        c = 0
        for dx, dy in neigh:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obstacles:
                c += 1
        return c

    if not resources:
        # Default: move to maximize distance from opponent while staying safe
        best_move = (0, 0)
        best = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            sc = cheb(nx, ny, ox, oy) - 0.5 * obstacle_adjacency(nx, ny)
            if sc > best:
                best = sc
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # Pick target resource that we can reach sooner than opponent, and that is less "trap-prone"
    best_res = resources[0]
    best_res_sc = 10**18
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        trap = 0.2 * obstacle_adjacency(rx, ry)
        sc = ds - 0.35 * do + trap
        if sc < best_res_sc:
            best_res_sc = sc
            best_res = (rx, ry)

    tx, ty = best_res
    # Choose step that reduces distance to target; tie-break by avoiding obstacles and distancing from opponent
    best_move = (0, 0)
    best = 10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_to_t = cheb(nx, ny, tx, ty)
        d_from_op = cheb(nx, ny, ox, oy)
        adj = obstacle_adjacency(nx, ny)
        sc = d_to_t * 10 - d_from_op + adj * 0.7
        if sc < best:
            best = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
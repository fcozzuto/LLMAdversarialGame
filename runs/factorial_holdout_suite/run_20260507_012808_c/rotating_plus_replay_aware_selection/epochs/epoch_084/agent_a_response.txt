def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = [0, 0]
        best_key = (-10**9, 10**9)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            dself = cheb(nx, ny, tx, ty)
            key = (-dself, dself)
            if key > best_key:
                best_key = key
                best = [dx, dy]
        return best

    res = [tuple(r) for r in resources]
    # Choose a move by looking at the best resource after moving one step.
    best_move = [0, 0]
    best_key = (-10**18, -10**18, 10**18)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        best_for_move = None
        for rx, ry in res:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach earlier; if tied, prefer farther from opponent.
            # Also slightly prefer shorter own distance to finish quicker.
            key = (-(sd - od), -od, sd)
            if best_for_move is None or key > best_for_move:
                best_for_move = key
        if best_for_move is None:
            continue
        # Global tie-break: prefer larger (-(sd-od)), then smaller own distance.
        global_key = (best_for_move[0], best_for_move[1], best_for_move[2])
        if global_key > best_key:
            best_key = global_key
            best_move = [dx, dy]
    return best_move
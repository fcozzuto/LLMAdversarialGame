def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (not inb(x, y)) or ((x, y) in obstacles)
    def man(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx + dy

    # If we have no visible resources, drift to center while keeping away from opponent
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        best_move = [0, 0]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if blocked(nx, ny): 
                continue
            key = (man(nx, ny, cx, cy), -man(nx, ny, ox, oy), dx, dy)
            if best is None or key < best:
                best, best_move = key, [dx, dy]
        return best_move

    # Pick best next step towards a resource with contest-aware heuristic
    best_key = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        my_best = None
        # minimize "advantage": being closer than opponent to same target resource
        for rx, ry in resources:
            dm = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            # Prefer resources where we can arrive earlier; also avoid letting opponent arrive too close.
            # Add tiny tie-breakers for determinism.
            key_res = (dm - do, dm, do, rx, ry)
            if my_best is None or key_res < my_best:
                my_best = key_res
        # Secondary objective: keep some distance from opponent while moving (helps corner_guard)
        opp_pen = -man(nx, ny, ox, oy)  # larger distance => smaller penalty
        key = (my_best[0], my_best[1], my_best[2] + opp_pen // 4, dx, dy)
        if best_key is None or key < best_key:
            best_key, best_move = key, [dx, dy]
    return best_move
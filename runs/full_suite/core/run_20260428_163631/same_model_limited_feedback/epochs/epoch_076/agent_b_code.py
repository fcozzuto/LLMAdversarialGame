def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    if resources:
        best_move = (0, 0)
        best_val = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            my_best_gap = -10**18
            my_min = 10**9
            for rx, ry in resources:
                my_d = cheb(nx, ny, rx, ry)
                op_d = cheb(ox, oy, rx, ry)
                if my_d < my_min: my_min = my_d
                gap = op_d - my_d  # positive means we are closer than opponent
                if gap > my_best_gap: my_best_gap = gap
            # Favor moves that win the race to some resource; tie-break by being closer overall and safer.
            opp_d_now = cheb(nx, ny, ox, oy)
            val = my_best_gap * 1000 - my_min * 5 + opp_d_now * 0.5
            # Deterministic tie-break by move ordering
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # No resources: drift toward your side's center to maintain tempo.
    cx, cy = (2, 2) if sx < w // 2 else (w - 3, h - 3)
    best = (0, 0)
    bestd = 10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = cheb(nx, ny, cx, cy)
        if d < bestd:
            bestd = d
            best = (dx, dy)
    return [best[0], best[1]]
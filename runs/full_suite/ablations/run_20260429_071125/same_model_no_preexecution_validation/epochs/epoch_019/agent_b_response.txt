def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    resources = observation.get("resources") or []

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = dx if dx >= 0 else -dx
        dy = y1 - y2; dy = dy if dy >= 0 else -dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    best_score = -10**18
    best_move = (0, 0)

    # If no resources, drift toward center.
    if not resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        tx, ty = int(cx + 0.5), int(cy + 0.5)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            score = -cheb(nx, ny, tx, ty)
            if score > best_score:
                best_score = score; best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # Main heuristic: compete for resources (our closeness vs opponent).
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        move_score = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles or not inb(rx, ry):
                continue
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer being closer than opponent; also prefer nearer overall.
            adv = do - ds
            s = adv * 100 - ds
            # Small tie-breaker: steer away from obstacles nearby.
            if (nx+1, ny) in obstacles or (nx-1, ny) in obstacles or (nx, ny+1) in obstacles or (nx, ny-1) in obstacles:
                s -= 5
            if s > move_score:
                move_score = s
        if move_score > best_score:
            best_score = move_score; best_move = (dx, dy)

    return [best_move[0], best_move[1]]
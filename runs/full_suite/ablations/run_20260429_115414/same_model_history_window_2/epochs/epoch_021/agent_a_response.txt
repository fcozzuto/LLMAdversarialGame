def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    rem = observation.get("remaining_resource_count", len(resources))

    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return inb(x, y) and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    # Choose a target resource: prefer ones we are closer to than opponent
    if rem > 0 and resources:
        best = None
        best_key = None  # maximize key
        parity = observation.get("turn_index", 0) & 1
        for i, r in enumerate(resources):
            rx, ry = r
            if (rx, ry) in blocked:
                continue
            du = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            margin = do - du
            # If tied or worse, slightly prefer nearer resources (to reduce opponent races)
            key = (margin, -du, (i & 1) ^ parity, -cheb(ox, oy, rx, ry))
            if best is None or key > best_key:
                best = (rx, ry)
                best_key = key
        tx, ty = best
    else:
        # No resources: contest by moving toward opponent
        tx, ty = ox, oy

    # Score each move with: progress to target + avoid being too close to opponent
    best_move = None
    best_score = -10**18
    for dx, dy, nx, ny in legal:
        d_t = cheb(nx, ny, tx, ty)
        d_o = cheb(nx, ny, ox, oy)
        # If pursuing resources, prefer staying at least mildly away from opponent to avoid swaps
        avoid = 0.6 if (rem > 0 and resources) else 0.1
        progress = -d_t
        # Nudge deterministic tie-break by position parity
        tie = -((nx + ny) & 1) * 0.01
        score = progress + avoid * d_o + tie
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]
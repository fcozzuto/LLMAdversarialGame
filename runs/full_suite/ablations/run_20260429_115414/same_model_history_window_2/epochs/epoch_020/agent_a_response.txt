def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    remaining = observation.get("remaining_resource_count", len(resources))

    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return inb(x, y) and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    # If no resources remain, contest by moving to minimize distance to opponent
    if remaining <= 0 or not resources:
        best = None; bestv = -10**18
        for dx, dy, nx, ny in legal:
            v = -cheb(nx, ny, ox, oy) - 0.05 * cheb(nx, ny, sx, sy)
            if v > bestv:
                bestv = v; best = (dx, dy)
        return [best[0], best[1]]

    # Choose a target resource that we can reach earlier than the opponent (deterministically tie-break by position)
    best_t = None; best_score = -10**18
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Favor closeness and "taking the race"; lightly prefer farther-from-opponent to reduce their access
        score = (do - ds) * 10 - ds - 0.1 * (rx + ry)
        if score > best_score:
            best_score = score
            best_t = (rx, ry)

    tx, ty = best_t
    # Defensive reroute: if opponent is extremely closer to the chosen target, pick a different one by reusing evaluation on move
    best = None; bestv = -10**18
    for dx, dy, nx, ny in legal:
        ds_n = cheb(nx, ny, tx, ty)
        # Estimate immediate desirability: get closer to target, deny opponent progress on same target, and avoid being trapped (closer to center slightly)
        denom = cheb(nx, ny, ox, oy) + 1
        v = -ds_n * 2 + (cheb(ox, oy, tx, ty) - ds_n) * 1.2
        v += 0.15 * (cheb(nx, ny, (w - 1) // 2, (h - 1) // 2) * -1)
        # If opponent can reach target much sooner, override with local race-to-best resource using same move
        if (cheb(ox, oy, tx, ty) - cheb(sx, sy, tx, ty)) > 2:
            v2 = -10**9
            for rx, ry in resources:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                score = (do - ds) * 10 - ds - 0.1 * (rx + ry)
                if score > v2:
                    v2 = score
            v = v2
        if v > bestv:
            bestv = v; best = (dx, dy)

    return [best[0], best[1]]
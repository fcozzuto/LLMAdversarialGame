def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = [tuple(p) for p in (observation.get("resources", []) or []) if tuple(p) not in obstacles]
    if not resources:
        return [0, 0]

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx >= dy else dy

    res_sorted = sorted(resources, key=lambda p: cheb(sx, sy, p[0], p[1]))[:8]

    best = (0, 0); best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        val = 0
        if (nx, ny) in obstacles:
            continue
        if (nx, ny) in resources:
            val += 10**7

        # Prefer resources we can get first; penalize ones opponent is closer to.
        # Also add a small "threat" term: moving that reduces opponent's advantage.
        for i, (rx, ry) in enumerate(res_sorted):
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            lead = opd - myd  # positive means we are closer
            # Closer resources get higher base weight
            base = 2000 // (1 + cheb(sx, sy, rx, ry))
            if lead >= 0:
                val += base * (1 + lead) * (10 - i)
            else:
                val -= base * (1 - lead) * (8 - i)
                # Extra denial pressure if opponent is significantly nearer
                if (-lead) >= 2:
                    val -= base * 3

        # Gentle obstacle-field avoidance: steer toward more open local area
        open_ct = 0
        for mdx, mdy in moves:
            tx, ty = nx + mdx, ny + mdy
            if inb(tx, ty) and (tx, ty) not in obstacles:
                open_ct += 1
        val += open_ct * 2

        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [best[0], best[1]]
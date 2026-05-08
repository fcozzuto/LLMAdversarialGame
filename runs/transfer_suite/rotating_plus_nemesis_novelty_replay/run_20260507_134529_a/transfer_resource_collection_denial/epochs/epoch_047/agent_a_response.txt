def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    if not resources:
        best = (0, 0, -10**9)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny): nx, ny = sx, sy
            v = cheb(nx, ny, ox, oy)
            if v > best[2]:
                best = (dx, dy, v)
        return [best[0], best[1]]

    best_move = (0, 0, -10**18)
    # If opponent is very close, prioritize evasion; otherwise pursue stealing via immediate advantage.
    opp_close = cheb(sx, sy, ox, oy) <= 2

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny): nx, ny = sx, sy

        if opp_close:
            # Evasion: maximize distance, but don't ignore nearby resources completely.
            dist = cheb(nx, ny, ox, oy)
            near = 10**18
            for rx, ry in resources:
                d = cheb(nx, ny, rx, ry)
                if d < near: near = d
            val = dist * 1000 - near
        else:
            # Pursuit: for the best resource, maximize (opponent_lead - self_distance) and prefer shorter paths.
            val = -10**18
            for rx, ry in resources:
                ds1 = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                advantage = do - ds1  # positive means we can arrive earlier/equal
                cand = advantage * 1000 - ds1
                if cand > val:
                    val = cand

        if val > best_move[2]:
            best_move = (dx, dy, val)

    return [best_move[0], best_move[1]]
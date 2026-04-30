def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = {(p[0], p[1]) for p in obstacles}
    res_set = {(r[0], r[1]) for r in resources}

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (not inb(x, y)) or ((x, y) in obs)
    def man(a, b, c, d): 
        dx = a - c; 
        return (dx if dx >= 0 else -dx) + ((b - d) if b >= d else (d - b))
    def cheb(a, b, c, d):
        dx = a - c; dx = dx if dx >= 0 else -dx
        dy = b - d; dy = dy if dy >= 0 else -dy
        return dx if dx > dy else dy
    def near_obstacle(x, y):
        cnt = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obs: cnt += 1
        return cnt

    if blocked(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]

    # If no resources visible, move away from opponent and away from obstacles edges deterministically.
    if not resources:
        best_score = -10**18; best = (0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if blocked(nx, ny): continue
            # Prefer increasing distance to opponent and decreasing obstacle proximity
            score = (man(nx, ny, ox, oy) * 2) - (near_obstacle(nx, ny) * 3) - cheb(nx, ny, ox, oy)
            if score > best_score or (score == best_score and (dx, dy) < best):
                best_score = score; best = (dx, dy)
        return [best[0], best[1]]

    # Score move by best advantage on any resource: (opp_dist - my_dist).
    best_score = -10**18; best = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny): continue

        my_best_adv = -10**18
        my_best_dist = 10**9
        for rx, ry in resources:
            # Chebyshev models how quickly you can collect with 8-neighbor movement
            md = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - md
            if adv > my_best_adv:
                my_best_adv = adv
            if md < my_best_dist:
                my_best_dist = md

        # Small tie-breakers: grab if landing on resource, avoid obstacle-adjacent cells,
        # and avoid moving into immediate opponent-capture proximity.
        on_resource = 1 if (nx, ny) in res_set else 0
        opp_prox = 1 if cheb(nx, ny, ox, oy) <= 1 else 0
        score = (my_best_adv * 100) + (on_resource * 100000) - (my_best_dist * 7) - (near_obstacle(nx, ny) * 5) - (opp_prox * 40)

        if score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score; best = (dx, dy)

    return [best[0], best[1]]
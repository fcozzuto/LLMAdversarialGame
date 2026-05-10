def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    role = (observation.get("self_role") or "").lower()
    is_pursuer = ("pursuer" in role) and ("evader" not in role)

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    corners = [(0,0),(0,h-1),(w-1,0),(w-1,h-1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_corner_from(px, py, want_farthest):
        best = corners[0]
        bestd = cheb(px, py, corners[0][0], corners[0][1])
        for cx, cy in corners[1:]:
            d = cheb(px, py, cx, cy)
            if want_farthest:
                if d > bestd:
                    bestd = d
                    best = (cx, cy)
            else:
                if d < bestd:
                    bestd = d
                    best = (cx, cy)
        return best

    self_to_esc = best_corner_from(sx, sy, True)  # where evader would like to head (far from pursuer)
    escx, escy = self_to_esc
    nearest_corner_to_opp = best_corner_from(ox, oy, False)
    ncx, ncy = nearest_corner_to_opp

    oldd = cheb(sx, sy, ox, oy)
    best_move = (0, 0)
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_ = cheb(nx, ny, ox, oy)

        if is_pursuer:
            # Move to reduce distance AND steer toward likely escape corner to limit options.
            primary = (oldd - d_)  # higher is better
            steer = -cheb(nx, ny, escx, escy)  # higher is better (closer to escape corner)
            cut = -cheb(nx, ny, ncx, ncy)    # extra bias toward opponent corner pressure
            score = (primary, steer, cut, -cheb(nx, ny, ox, oy))
        else:
            # Evader: maximize distance and head toward farthest corner from pursuer.
            primary = (d_ - oldd)
            flee = cheb(nx, ny, escx, escy)  # farther from pursuer-chosen escape anchor
            toward = -cheb(nx, ny, ncx, ncy)  # also keep some direction toward opponent-nearest corner
            score = (primary, flee, toward, d_)

        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
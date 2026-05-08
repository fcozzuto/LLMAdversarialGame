def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = [tuple(r) for r in (observation.get("resources", []) or []) if tuple(r) not in obstacles]
    if not resources:
        return [0, 0]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx >= dy else dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        best_res_score = -10**18
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            race = (opd - myd)  # positive => I closer
            res_score = race * 100 - myd  # prioritize winning race, then speed

            # small anti-interference: if opponent is also close, prefer resources that keep me nearer
            inter = cheb(ox, oy, rx, ry) - myd
            res_score += inter * 2

            # stepping onto resource is best (if resource list includes it, engine likely removes next)
            if myd == 0:
                res_score += 10000
            if res_score > best_res_score:
                best_res_score = res_score

        # keep away from opponent to reduce their races slightly (ties only)
        opp_dist = cheb(nx, ny, ox, oy)
        total = best_res_score + opp_dist * 0.5

        if total > best_score:
            best_score = total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
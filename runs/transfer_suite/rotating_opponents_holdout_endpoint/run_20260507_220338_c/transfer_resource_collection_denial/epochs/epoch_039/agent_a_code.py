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
    best = (0, 0, -10**18)  # dx,dy,score

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        cell_is_res = 1 if (nx, ny) in resources else 0

        best_cell = -10**18
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            race = opd - myd  # positive means I'm closer or tie-break favorable
            res_score = race * 120 - myd * 3 + cell_is_res * 2000

            # Prefer resources that opponent can't reach as fast (or at all)
            if opd < myd:
                res_score -= (myd - opd) * 60
            elif opd == myd:
                res_score += 15

            # Slightly prefer staying on paths that reduce my distance to the "frontier" resources
            # by rewarding moves that also move closer to the best resource by my distance.
            res_score += max(0, 6 - myd)

            if res_score > best_cell:
                best_cell = res_score

        # Mild penalty for moving away from the closest resource from current position
        cur_best = min(cheb(sx, sy, rx, ry) for rx, ry in resources)
        nxt_best = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
        best_cell -= max(0, nxt_best - cur_best) * 8

        if best_cell > best[2]:
            best = (dx, dy, best_cell)

    return [best[0], best[1]]
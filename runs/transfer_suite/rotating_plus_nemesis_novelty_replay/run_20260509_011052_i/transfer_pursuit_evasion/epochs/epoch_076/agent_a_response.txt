def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    role = (observation.get("self_role") or "").lower()
    is_pursuer = ("pursuer" in role) and ("evader" not in role)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def nearest_corner(px, py):
        best = corners[0]
        bestd = cheb(px, py, best[0], best[1])
        for cx, cy in corners[1:]:
            d = cheb(px, py, cx, cy)
            if d < bestd:
                bestd = d
                best = (cx, cy)
        return best

    def farthest_corner(px, py):
        best = corners[0]
        bestd = cheb(px, py, best[0], best[1])
        for cx, cy in corners[1:]:
            d = cheb(px, py, cx, cy)
            if d > bestd:
                bestd = d
                best = (cx, cy)
        return best

    if is_pursuer:
        tcx, tcy = nearest_corner(ox, oy)  # likely corner evader targets
        best_move = (0, 0)
        best_score = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d_opp = cheb(nx, ny, ox, oy)
            d_corner = cheb(nx, ny, tcx, tcy)
            score = (d_opp, d_corner, abs(nx - ox) + abs(ny - oy))
            if best_score is None or score < best_score:
                best_score = score
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]
    else:
        tcx, tcy = farthest_corner(sx, sy)  # head to far corner
        # If pursuer is already closer to that corner, instead pick the corner farthest from pursuer
        if cheb(tcx, tcy, ox, oy) <= cheb(nearest_corner(sx, sy)[0], nearest_corner(sx, sy)[1], ox, oy):
            tcx, tcy = farthest_corner(ox, oy)
        best_move = (0, 0)
        best_score = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d_opp = cheb(nx, ny, ox, oy)
            d_corner = cheb(nx, ny, tcx, tcy)
            score = (-d_opp, d_corner, abs(nx - ox) + abs(ny - oy))
            if best_score is None or score < best_score:
                best_score = score
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]
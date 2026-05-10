def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obs = set(tuple(p) for p in (observation.get("obstacles") or []))

    role = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role)
    is_pursuer = ("pursuer" in role) or ("chaser" in role) or (not is_evader)

    moves = [(-1, -1), (0, -1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def adj_obs(x, y):
        c = 0
        for nx in (x - 1, x, x + 1):
            if nx < 0 or nx >= w: 
                continue
            for ny in (y - 1, y, y + 1):
                if ny < 0 or ny >= h:
                    continue
                if (nx, ny) in obs:
                    c += 1
        return c

    def nearest_corner_to(tx, ty):
        best = corners[0]
        bd = cheb(tx, ty, best[0], best[1])
        for cx, cy in corners[1:]:
            d = cheb(tx, ty, cx, cy)
            if d < bd:
                bd, best = d, (cx, cy)
        return best

    if is_pursuer:
        target_corner = nearest_corner_to(ox, oy)  # chase-and-cut toward evader's corner
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d_opp = cheb(nx, ny, ox, oy)
            d_corner = cheb(nx, ny, target_corner[0], target_corner[1])
            # lower is better
            score = d_opp * 10 + d_corner + adj_obs(nx, ny) * 0.05
            cand = (score, abs(dx) + abs(dy), dx, dy)
            if best is None or cand < best:
                best = cand
        return [best[2], best[3]] if best is not None else [0, 0]
    else:
        # evade: move toward corner farthest from pursuer, avoid obstacles, and keep distance
        target_corner = nearest_corner_to(ox, oy)
        far_corner = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d_opp = cheb(nx, ny, ox, oy)
            d_corner = cheb(nx, ny, far_corner[0], far_corner[1])
            # higher is better
            score = d_opp * 10 - d_corner - adj_obs(nx, ny) * 0.08
            cand = (-score, abs(dx) + abs(dy), dx, dy)  # minimize for tie-break
            if best is None or cand < best:
                best = cand
        return [best[2], best[3]] if best is not None else [0, 0]
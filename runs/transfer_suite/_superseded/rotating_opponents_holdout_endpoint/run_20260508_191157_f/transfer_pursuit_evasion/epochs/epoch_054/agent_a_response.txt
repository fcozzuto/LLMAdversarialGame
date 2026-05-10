def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    role = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role)
    # if not explicitly evader, assume pursuer-like
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def adj_obs(x, y):
        c = 0
        for nx in (x - 1, x, x + 1):
            if nx < 0 or nx >= w:
                continue
            for ny in (y - 1, y, y + 1):
                if ny < 0 or ny >= h:
                    continue
                if (nx, ny) in obstacles:
                    c += 1
        return c

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    def best_corner_score(px, py):
        # higher is better for evader
        bd = cheb(px, py, corners[0][0], corners[0][1])
        for cx, cy in corners[1:]:
            d = cheb(px, py, cx, cy)
            if d > bd: bd = d
        # prefer being far from center bottlenecks implicitly by corner distance
        return bd

    best = None
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        d_now = cheb(sx, sy, ox, oy)
        d_new = cheb(nx, ny, ox, oy)

        a = adj_obs(nx, ny)

        if is_evader:
            # evade: maximize distance and avoid tight corners/walls; also steer to farthest corner from opponent
            corner_term = 0
            for cx, cy in corners:
                corner_term += 0  # deterministic placeholder elimination
            # score based on maximizing opponent-corner distance proxy
            opp_corner_d = -1
            for cx, cy in corners:
                od = cheb(ox, oy, cx, cy)
                if od > opp_corner_d: opp_corner_d = od
            my_corner_d = best_corner_score(nx, ny)
            score = (d_new - d_now) * 10 + d_new * 2 + my_corner_d - a * 0.7 - cheb(nx, ny, ox, oy) * 0.05 - opp_corner_d * 0.01
        else:
            # pursue: minimize distance, prefer moves reducing it; avoid walls
            capture_bonus = 1000 if (nx == ox and ny == oy) else 0
            score = -((d_new - d_now) * 10 + d_new * 2) - a * 0.3 + capture_bonus

        if best is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best
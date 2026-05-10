def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    self_is_evader = ("evader" in self_role) or ("evasion" in self_role) or ("runner" in self_role)
    opp_is_evader = ("evader" in opp_role) or ("evasion" in opp_role) or ("runner" in opp_role)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist_cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    chase = (not self_is_evader) and opp_is_evader
    if self_is_evader and not opp_is_evader:
        chase = False

    if chase:
        best = None
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            v = dist_cheb(nx, ny, ox, oy)  # minimize
            if bestv is None or v < bestv:
                bestv = v
                best = (dx, dy)
        return list(best if best is not None else (0, 0))
    else:
        corners = [(0, 0), (w - 1, 0), (w - 1, h - 1), (0, h - 1)]
        tx, ty = corners[0]
        bestd = -1
        for cx, cy in corners:
            d = dist_cheb(cx, cy, ox, oy)
            if d > bestd:
                bestd = d
                tx, ty = cx, cy

        best = None
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            d_to_target = dist_cheb(nx, ny, tx, ty)  # maximize progress to far corner
            d_away = dist_cheb(nx, ny, ox, oy)  # also maximize distance from pursuer
            v = (d_to_target * 100 + d_away)  # deterministic scalar
            if bestv is None or v > bestv:
                bestv = v
                best = (dx, dy)
        return list(best if best is not None else (0, 0))
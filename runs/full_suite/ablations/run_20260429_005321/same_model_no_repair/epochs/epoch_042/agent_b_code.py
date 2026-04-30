def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obs)

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def adj_obs_pen(x, y):
        p = 0
        for dxi in (-1, 0, 1):
            for dyi in (-1, 0, 1):
                if dxi == 0 and dyi == 0:
                    continue
                if (x + dxi, y + dyi) in obs:
                    p += 1
        return p

    opp_dist_now = king_dist(sx, sy, ox, oy)
    prefer_intercept = (resources and len(resources) <= 3 and opp_dist_now <= 2) or (not resources)

    if not resources:
        tx, ty = ox, oy
    elif prefer_intercept:
        # Intercept by heading to the closest resource that is also close to opponent
        best = None
        bestv = None
        for rx, ry in resources:
            d1 = king_dist(sx, sy, rx, ry)
            d2 = king_dist(ox, oy, rx, ry)
            v = (d1 * 10 + d2) + adj_obs_pen(rx, ry) * 3
            if best is None or v < bestv or (v == bestv and (rx, ry) < best):
                best = (rx, ry)
                bestv = v
        tx, ty = best
    else:
        # Take resource that is near us but far from opponent
        best = None
        bestv = None
        for rx, ry in resources:
            d1 = king_dist(sx, sy, rx, ry)
            d2 = king_dist(ox, oy, rx, ry)
            v = (d1 * 10 - d2 * 6) + adj_obs_pen(rx, ry) * 3
            if best is None or v < bestv or (v == bestv and (rx, ry) < best):
                best = (rx, ry)
                bestv = v
        tx, ty = best

    cand = []
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if blocked(nx, ny):
            continue
        step_to = king_dist(nx, ny, tx, ty)
        opp_step = king_dist(nx, ny, ox, oy)
        # Prefer reducing distance to target, while not wandering near obstacles; slight anti-approach when not intercepting
        score = step_to * 10 + adj_obs_pen(nx, ny) * 2 + (0 if prefer_intercept else opp_step * 1)
        # tie-break deterministically by move order
        cand.append((score, mx, my, step_to, nx, ny))

    if not cand:
        return [0, 0]
    cand.sort()
    return [cand[0][1], cand[0][2]]
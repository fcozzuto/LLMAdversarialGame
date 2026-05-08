def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obs

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    # Deterministically pick candidate resources (closest to either player), then score moves.
    cand_res = []
    for r in resources:
        rx, ry = r[0], r[1]
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        cand_res.append((min(sd, od), sd, od, rx, ry))
    cand_res.sort()
    cand_res = cand_res[:6] if len(cand_res) > 6 else cand_res
    if not cand_res:
        for d in dirs:
            nx, ny = sx + d[0], sy + d[1]
            if free(nx, ny):
                return [d[0], d[1]]
        return [0, 0]

    best = None
    for d in dirs:
        nx, ny = sx + d[0], sy + d[1]
        if not free(nx, ny):
            continue
        score = 0
        # Maximize (opponent_distance - self_distance) to the best target; break ties deterministically.
        local_best = None
        for _, sd, od, rx, ry in cand_res:
            sdn = cheb(nx, ny, rx, ry)
            odn = od - sd + od  # stable-ish but avoid dependence; will be overwritten by exact below
            odn = cheb(ox, oy, rx, ry)
            adv = odn - sdn
            key = (adv, -sdn, -odn, rx, ry)
            if local_best is None or key > local_best:
                local_best = key
        score = local_best
        if best is None or score > best:
            best = score
            best_move = d

    if best is None:
        return [0, 0]
    return [best_move[0], best_move[1]]
def choose_move(observation):
    w = observation.get("grid_width", 0) or 0
    h = observation.get("grid_height", 0) or 0
    try:
        w = int(w); h = int(h)
    except:
        return [0, 0]
    if w <= 0 or h <= 0:
        return [0, 0]

    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    if not resources:
        best = (-10**18, 0, 0)
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            val = -cheb(nx, ny, ox, oy)  # minimize distance to opponent
            if val > best[0]:
                best = (val, dx, dy)
        return [best[1], best[2]]

    best = (-10**18, 0, 0)
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        best_adv = -10**18
        min_dist = 10**18
        for rx, ry in resources:
            our_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            adv = opp_d - our_d  # positive if we are closer/equal
            if adv > best_adv:
                best_adv = adv
            if our_d < min_dist:
                min_dist = our_d
        val = best_adv * 10 - min_dist
        if val > best[0]:
            best = (val, dx, dy)
    return [best[1], best[2]]
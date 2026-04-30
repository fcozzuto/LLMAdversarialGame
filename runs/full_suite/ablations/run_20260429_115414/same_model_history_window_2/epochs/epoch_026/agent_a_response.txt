def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def adj_pen(x, y):
        pen = 0
        if not blocked:
            return 0
        for bx, by in blocked:
            if abs(bx - x) <= 1 and abs(by - y) <= 1:
                pen += 2
        return pen

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources or observation.get("remaining_resource_count", 0) <= 0:
        best = None
        for dx, dy, nx, ny in legal:
            cand = (cheb(nx, ny, ox, oy), -adj_pen(nx, ny), -nx, -ny, dx, dy)
            if best is None or cand > best:
                best = cand
        return [best[4], best[5]]

    res = [(int(x), int(y)) for x, y in resources]
    best_overall = None
    for dx, dy, nx, ny in legal:
        # Choose the resource that gives the best access advantage (opponent farther than us).
        best_adv = None
        for rx, ry in res:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds
            cand = (adv, -ds, -abs(nx - rx) - abs(ny - ry))
            if best_adv is None or cand > best_adv:
                best_adv = cand
        adv, neg_ds, _ = best_adv
        dist_to_opp = cheb(nx, ny, ox, oy)
        cand_move = (adv, neg_ds, dist_to_opp, -adj_pen(nx, ny), -nx, -ny, dx, dy)
        if best_overall is None or cand_move > best_overall:
            best_overall = cand_move

    return [best_overall[6], best_overall[7]]
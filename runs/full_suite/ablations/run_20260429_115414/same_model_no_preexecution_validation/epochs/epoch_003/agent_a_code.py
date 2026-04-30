def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal_moves_from(x, y):
        res = []
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                res.append((dx, dy, nx, ny))
        return res

    lm_self = legal_moves_from(sx, sy)
    if not lm_self:
        return [0, 0]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (10**18, 0, 0)
        for dx, dy, nx, ny in lm_self:
            key = (cheb(nx, ny, tx, ty), abs(dx)+abs(dy), dx, dy)
            if key < best:
                best = key
        return [best[2], best[3]]

    best_key = (-10**18, 0, 0, 0)  # (score, -ourDist, dx, dy)
    for sdx, sdy, nx, ny in lm_self:
        # compute our best target score against opponent for each resource
        best_for_move = -10**18
        best_dist = 10**18
        for rx, ry in resources:
            our_d = cheb(nx, ny, rx, ry)
            # opponent can move one step; estimate best reachable distance
            opp_best = 10**18
            for odx, ody, onx, ony in legal_moves_from(ox, oy):
                d = cheb(onx, ony, rx, ry)
                if d < opp_best:
                    opp_best = d
            opp_d = opp_best
            # prefer resources we can reach at least not worse, and that are closer
            adv = opp_d - our_d
            # slight tie-break: prefer closer resource and moving toward it consistently
            val = adv * 100 - our_d
            if our_d < best_dist:
                best_dist = our_d
            if val > best_for_move:
                best_for_move = val
        # add penalty if we would be stuck far from all resources
        min_d = best_dist
        key = (best_for_move, -min_d, sdx, sdy)
        if key > best_key:
            best_key = key

    return [best_key[2], best_key[3]]
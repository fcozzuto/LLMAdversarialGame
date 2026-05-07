def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx = gw - 1 if sx < gw // 2 else 0
        ty = gh - 1 if sy < gh // 2 else 0
        best = (0, 0, -10**18)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            v = -d
            if v > best[2]:
                best = (dx, dy, v)
        return [best[0], best[1]]

    best_dx, best_dy, best_val = 0, 0, -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        our_d = cheb(nx, ny, nx, ny)
        # Evaluate by best target from this candidate position
        cand_val = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d_me = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach sooner; small bias toward closer ones
            # Also penalize giving opponent a shorter route
            v = (d_op - d_me) * 10 - d_me
            # Strongly prefer landing on a resource immediately if possible
            if d_me == 0:
                v += 1000
            if v > cand_val:
                cand_val = v
        # If multiple moves tie, prefer moving toward increasing distance from opponent
        # to reduce contention in resource_denier pools.
        opp_dist = cheb(nx, ny, ox, oy)
        tie_break = opp_dist * 0.01
        total = cand_val + tie_break
        if total > best_val:
            best_val = total
            best_dx, best_dy = dx, dy

    return [best_dx, best_dy]
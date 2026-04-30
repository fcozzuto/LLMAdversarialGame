def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((x, y) for x, y in observation["obstacles"])
    resources = observation["resources"] if observation["resources"] else []
    occ = obstacles

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        tx, ty = w - 1 - sx, h - 1 - sy
        candidates = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
        best = (None, -10**9)
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in occ:
                continue
            score = -(abs(nx - tx) + abs(ny - ty))
            if score > best[1]:
                best = ((dx, dy), score)
        return best[0] if best[0] is not None else [0, 0]

    opp = (ox, oy)
    best_target = None
    best_adv = -10**18
    for rx, ry in resources:
        sr = dist((sx, sy), (rx, ry))
        orr = dist(opp, (rx, ry))
        # Prefer resources we can reach sooner; deny those opponent is close to.
        adv = orr - sr
        if sr == 0:
            adv = 10**9
        if adv > best_adv:
            best_adv = adv
            best_target = (rx, ry)

    tx, ty = best_target
    candidates = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in occ:
            val = -10**12
        else:
            d_self = dist((nx, ny), (tx, ty))
            d_opp = dist(opp, (tx, ty))
            # Keep progressing; also discourage moves that give opponent an advantage.
            deny = d_opp - d_self
            # Small tie-breakers: avoid drifting away from centerline to target and keep some spacing from opponent.
            opp_close = 7 - dist((nx, ny), opp)
            val = (10**6 if (nx, ny) == (tx, ty) else 0) + deny * 1000 - d_self * 10 - opp_close * 2
            # Discourage stepping near obstacles (soft)
            for ax, ay in ((nx-1, ny), (nx+1, ny), (nx, ny-1), (nx, ny+1)):
                if (ax, ay) in occ:
                    val -= 8
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]
def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(a, b, c, d):
        ax, ay, bx, by = int(a), int(b), int(c), int(d)
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    cx, cy = (w - 1) // 2, (h - 1) // 2
    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    best_move = [0, 0]
    best_score = -10**18
    best_tiebreak = 10**18

    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not inside(nx, ny):
            continue
        # Choose the resource that gives the biggest advantage from this candidate next position.
        local_best_adv = -10**18
        local_best_dist = 10**18
        for tx, ty in resources:
            ds = cheb(nx, ny, tx, ty)
            do = cheb(ox, oy, tx, ty)
            # Advantage: we want opponent farther than us; also drift toward center.
            adv = (do - ds) - 0.15 * cheb(nx, ny, cx, cy)
            if adv > local_best_adv or (adv == local_best_adv and ds < local_best_dist):
                local_best_adv = adv
                local_best_dist = ds
        # Prefer moves that keep (overall) advantage high, then reduce our distance to the chosen best target.
        center_bias = -0.01 * cheb(nx, ny, cx, cy)
        score = local_best_adv + center_bias
        if score > best_score or (score == best_score and local_best_dist < best_tiebreak):
            best_score = score
            best_tiebreak = local_best_dist
            best_move = [mx, my]

    return [int(best_move[0]), int(best_move[1])]
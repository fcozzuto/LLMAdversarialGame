def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def center_target():
        return (w - 1) // 2, (h - 1) // 2

    if not resources:
        tx, ty = center_target()
        best = [0, 0]
        bestd = 10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                d = cheb(nx, ny, tx, ty)
                if d < bestd:
                    bestd = d
                    best = [dx, dy]
        return best

    ox, oy = observation["opponent_position"]
    res = [tuple(r) for r in resources]

    best_move = [0, 0]
    best_score = -10**18
    best_tiebreak = 10**9

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Choose the resource that gives us the highest closeness advantage after this move.
        # Advantage: opp_dist - our_dist (larger => we are closer).
        max_adv = -10**18
        min_my_dist = 10**9
        for rx, ry in res:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = opd - myd
            if adv > max_adv or (adv == max_adv and myd < min_my_dist):
                max_adv = adv
                min_my_dist = myd

        # Prefer moving onto a resource if possible; otherwise prefer smallest my distance among best-adv.
        on_resource = 1 if (nx, ny) in obstacles else 0
        score = max_adv * 1000 - min_my_dist
        if score > best_score or (score == best_score and min_my_dist < best_tiebreak):
            best_score = score
            best_tiebreak = min_my_dist
            best_move = [dx, dy]

    return best_move
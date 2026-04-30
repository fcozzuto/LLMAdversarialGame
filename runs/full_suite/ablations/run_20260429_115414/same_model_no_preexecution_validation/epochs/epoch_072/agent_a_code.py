def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    opp_best = None
    opp_best_d = 10**9
    for tx, ty in resources:
        d = cheb(ox, oy, tx, ty)
        if d < opp_best_d or (d == opp_best_d and (tx < opp_best[0] if opp_best else True)):
            opp_best_d = d
            opp_best = (tx, ty)

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        my_min = 10**9
        my_adv = -10**9
        for tx, ty in resources:
            myd = cheb(nx, ny, tx, ty)
            opd = cheb(ox, oy, tx, ty)
            adv = (opd - myd)
            if adv > my_adv or (adv == my_adv and myd < my_min):
                my_adv = adv
            if myd < my_min:
                my_min = myd

        # Deny opponent's most immediate target by moving to worsen their access more than your own
        tx0, ty0 = opp_best
        deny = cheb(ox, oy, tx0, ty0) - cheb(ox, oy, tx0, ty0)  # constant baseline
        # Use indirect deny: prefer moves that bring you closer to that target (so you can contest/arrive)
        contest = -cheb(nx, ny, tx0, ty0)

        score = (my_adv * 1000) + contest * 10 - my_min
        if score > best_score or (score == best_score and my_min < cheb(sx, sy, tx0, ty0)):
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        return [0, 0]
    return [int(dx), int(dy)]
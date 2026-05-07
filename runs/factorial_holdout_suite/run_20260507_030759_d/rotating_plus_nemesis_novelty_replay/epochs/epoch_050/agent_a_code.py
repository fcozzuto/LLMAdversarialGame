def choose_move(observation):
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            cell = (int(r[0]), int(r[1]))
            if cell not in obstacles:
                resources.append(cell)
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx >= dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Choose a target resource that we can reach no slower than the opponent, weighted by distance.
    best_t = None
    best_key = (-10**9, -10**9)
    for tx, ty in resources:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        adv = od - sd  # positive means we're closer in Chebyshev
        key = (adv, -sd)
        if key > best_key:
            best_key = key
            best_t = (tx, ty)

    tx, ty = best_t
    # Evaluate moves by improving our advantage towards the chosen target, and safety against obstacles.
    best_m = [0, 0]
    best_v = (-10**18, -10**18)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        sd2 = cheb(nx, ny, tx, ty)
        od2 = cheb(ox, oy, tx, ty)
        adv2 = od2 - sd2
        # Secondary: prefer smaller self distance to any resource we can plausibly contest.
        alt_sd = 10**9
        for rx, ry in resources:
            d = cheb(nx, ny, rx, ry)
            if d < alt_sd:
                alt_sd = d
        v = (adv2, -alt_sd)
        if v > best_v:
            best_v = v
            best_m = [dx, dy]

    return best_m
def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    res_list = []
    res_set = set()
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            res_list.append((x, y))
            res_set.add((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not res_list:
        return [0, 0]

    # Choose a target resource that we are relatively closer to than the opponent.
    best_res = res_list[0]
    best_score = -10**18
    for rx, ry in res_list:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Encourage picking resources near us and where we are ahead; also avoid far targets.
        score = (opd - myd) * 100 - myd
        # If tied, prefer nearer to corner (deterministic mild tie-break)
        score += -(rx + ry)
        if score > best_score:
            best_score = score
            best_res = (rx, ry)

    rx, ry = best_res

    best_move = (0, 0)
    best_key = (-10**18, 10**18, 10**18)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        myd = cheb(nx, ny, rx, ry)
        opd = cheb(ox, oy, rx, ry)

        # If we move onto a resource, strongly prefer it.
        pick = 1 if (nx, ny) in res_set else 0

        # Also add pressure to reduce the opponent's advantage on that target.
        adv = (opd - myd)

        key = (pick * 10**12 + adv * 10**4 - myd, myd, 0 if (dx, dy) == (0, 0) else 1)
        # Deterministic tie-break by move order
        if key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
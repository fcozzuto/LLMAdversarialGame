def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            t = (int(r[0]), int(r[1]))
            if t not in obstacles:
                resources.append(t)

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Pick a couple of resources deterministically (closest to opponent first for denial)
    res_sorted = sorted(resources, key=lambda t: (man(ox, oy, t[0], t[1]), man(sx, sy, t[0], t[1]), t[0], t[1]))
    top1 = res_sorted[0]
    top2 = res_sorted[1] if len(res_sorted) > 1 else top1

    best = (-(10**18), 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        # Main: go to resources where we can out-approach opponent
        score = 0
        for rx, ry in (top1, top2):
            selfd = man(nx, ny, rx, ry)
            oppd = man(ox, oy, rx, ry)
            # Strongly prefer resources we are closer to now (after move)
            score += (oppd - selfd) * 6 - selfd * 1.2

            # Denial/tempo: if opponent is much closer, try to intercept along the line by targeting a midpoint-near
            if oppd <= selfd + 1:
                midx = (rx + ox) // 2
                midy = (ry + oy) // 2
                score += -man(nx, ny, midx, midy) * 0.9

        # Secondary: steer away from obstacles by mildly penalizing moves that reduce options
        neigh_free = 0
        for ddx, ddy in moves:
            tx, ty = nx + ddx, ny + ddy
            if in_bounds(tx, ty) and (tx, ty) not in obstacles:
                neigh_free += 1
        score += neigh_free * 0.05

        if score > best[0] or (score == best[0] and (dx, dy) < (best[1], best[2])):
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]
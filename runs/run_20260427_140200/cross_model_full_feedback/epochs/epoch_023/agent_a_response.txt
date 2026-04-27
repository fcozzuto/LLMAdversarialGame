def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]) or [0, 0])
    ox, oy = map(int, observation.get("opponent_position", [0, 0]) or [0, 0])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    resset = set()
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
                resset.add((x, y))

    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    free = lambda x, y: inb(x, y) and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    cur_min = min((md((sx, sy), r) for r in resources), default=999)
    opp_min = min((md((ox, oy), r) for r in resources), default=999)

    best = None
    for dx, dy, nx, ny in cand:
        my_min = min((md((nx, ny), r) for r in resources), default=999)
        my_dist_opp = md((nx, ny), (ox, oy))
        cur_opp_dist = md((sx, sy), (ox, oy))
        to_resource = 0 if cur_min == 999 else (cur_min - my_min)

        # deterministic "race": if we're ahead on distance to nearest resource, keep pushing;
        # if behind, prioritize reducing our distance while not giving opponent an easy approach.
        ahead = 1 if (cur_min <= opp_min) else -1
        score = 0
        score += 10 * to_resource
        if (nx, ny) in resset:
            score += 60
        score += 0.25 * my_dist_opp
        score += ahead * 2.0 * (my_min - opp_min)

        # avoid stepping into "adjacent contest" where opponent can immediately take/contest
        if md((nx, ny), (ox, oy)) <= 1:
            score -= 8

        # small tie-break to prefer staying in place less often when equal
        score -= 0.01 * (0 if (dx == 0 and dy == 0) else 1)

        if best is None or score > best[0]:
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]
def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def obstacle_adj(x, y):
        c = 0
        for dxx, dyy in deltas:
            tx, ty = x + dxx, y + dyy
            if (tx, ty) in obstacles:
                c += 1
        return c

    # Choose target deterministically: resource where we have the biggest distance advantage
    me = (sx, sy)
    opp = (ox, oy)
    target = None
    best_adv = None
    best_d = None
    if resources:
        for r in resources:
            da = dist(opp, r) - dist(me, r)
            d = dist(me, r)
            if (best_adv is None) or (da > best_adv) or (da == best_adv and d < best_d) or (da == best_adv and d == best_d and (r[0], r[1]) < (target[0], target[1])):
                target = r
                best_adv = da
                best_d = d

    if target is None:
        # No resources visible: drift toward center while avoiding obstacles
        center = (w // 2, h // 2)
        target = center

    best_move = legal[0]
    best_score = None
    for dx, dy, nx, ny in legal:
        d_to_t = dist((nx, ny), target)
        # stay away from opponent unless we can reduce our distance to target a lot
        d_to_opp = dist((nx, ny), opp)
        # keep away from obstacles/edges indirectly
        adj = obstacle_adj(nx, ny)
        # Prefer reducing distance to target; prefer increasing distance to opponent; avoid obstacle-adjacency
        score = (-2.0 * d_to_t) + (0.35 * d_to_opp) - (0.6 * adj)
        if (best_score is None) or (score > best_score) or (score == best_score and (dx, dy) == (best_move[0], best_move[1])):
            best_score = score
            best_move = (dx, dy, nx, ny)

    return [int(best_move[0]), int(best_move[1])]
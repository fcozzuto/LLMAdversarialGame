def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position") or (0, 0))
    ox, oy = map(int, observation.get("opponent_position") or (w - 1, h - 1))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = w // 2, h // 2
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        return [dx, dy]

    me = (sx, sy)
    opp = (ox, oy)

    def obs_pen(cell):
        x, y = cell
        pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                nx, ny = x + ax, y + ay
                if (nx, ny) in obstacles:
                    pen += 1
        return pen

    best = None
    for r in resources:
        myd = man(me, r)
        oppd = man(opp, r)
        # Prefer resources where we can arrive not much later than opponent, and penalize clutter near the resource.
        sc = (myd - 0.75 * oppd) + 0.06 * obs_pen(r) + 0.01 * (r[0] + r[1])
        if best is None or sc < best[0]:
            best = (sc, r)

    target = best[1]

    # Choose a legal move that most improves our distance to target; tie-break by increasing opponent distance.
    best_move = (10**9, -10**9, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        myd2 = man((nx, ny), target)
        oppd2 = man(opp, target)
        opp_dist_from_me = man((nx, ny), opp)
        # primary: minimize myd2; secondary: maximize spacing from opponent; tertiary: deterministic lexicographic.
        cand = (myd2, -opp_dist_from_me, dx, dy)
        if cand < (best_move[0], best_move[1], best_move[2], best_move[3]):
            best_move = (myd2, -opp_dist_from_me, dx, dy)

    return [int(best_move[2]), int(best_move[3])]
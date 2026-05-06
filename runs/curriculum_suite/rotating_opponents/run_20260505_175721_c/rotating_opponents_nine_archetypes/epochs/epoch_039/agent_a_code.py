def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Pick target maximizing relative advantage (opponent farther than we are)
    best_adv = -10**18
    best_t = resources[0]
    for tx, ty in resources:
        myd = man(sx, sy, tx, ty)
        opd = man(ox, oy, tx, ty)
        adv = opd - myd
        if adv > best_adv or (adv == best_adv and myd < man(sx, sy, best_t[0], best_t[1])):
            best_adv = adv
            best_t = (tx, ty)

    tx, ty = best_t

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def score_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            return -10**12
        myd2 = man(nx, ny, tx, ty)
        opd = man(ox, oy, tx, ty)
        adv2 = opd - myd2
        # Small tie-breakers: prefer progress toward target and away from obstacles
        prog = myd2 - man(sx, sy, tx, ty)
        obstacle_pen = 0
        for ax, ay in obstacles:
            if abs(ax - nx) <= 1 and abs(ay - ny) <= 1:
                obstacle_pen += 1
        return adv2 * 1000 - myd2 - 3 * prog - 10 * obstacle_pen

    best_s = -10**18
    best_m = (0, 0)
    for dx, dy in dirs:
        s = score_move(dx, dy)
        if s > best_s or (s == best_s and (dx, dy) < best_m):
            best_s = s
            best_m = (dx, dy)

    dx, dy = best_m
    return [int(dx), int(dy)]
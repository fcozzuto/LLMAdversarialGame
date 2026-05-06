def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [w - 1, h - 1]))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        # deterministic fallback: drift toward center-ish away from opponent
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (10**9, 10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            val = man(nx, ny, cx, cy) - 0.2 * man(nx, ny, ox, oy)
            if val < best[0]:
                best = (val, man(nx, ny, ox, oy), dx, dy)
        return [int(best[2]), int(best[3])]

    best = (10**18, 10**18, 10**18, 0, 0)  # (adv, sd, -od, dx, dy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # choose best resource this move would target by maximizing our advantage
        move_best = None  # (adv, sd, -od)
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = sd - od  # negative means we are closer/equal than opponent
            cand = (adv, sd, -od)
            if move_best is None or cand < move_best:
                move_best = cand
        # Prefer more winning advances; then closer self; then keep away from opponent if tied
        if move_best is None:
            continue
        if move_best < best[:3]:
            best = (move_best[0], move_best[1], move_best[2], dx, dy)

    return [int(best[3]), int(best[4])]
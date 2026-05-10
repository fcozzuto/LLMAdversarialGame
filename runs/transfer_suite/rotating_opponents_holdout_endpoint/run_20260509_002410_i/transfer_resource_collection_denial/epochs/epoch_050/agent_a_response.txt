def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    res = []
    for r in resources:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry) and (rx, ry) not in obstacles:
                res.append((rx, ry))
    if not res:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Opponent's current closest resource (for a mild "deny/pressure" bias)
    opp_target = min(res, key=lambda p: (man((ox, oy), p), -p[0], -p[1]))

    # Prefer resources we can arrive at no later than opponent; otherwise race by gain.
    best = None
    for r in res:
        sd = man((sx, sy), r)
        od = man((ox, oy), r)
        # lexicographic: first choose those we can beat or tie, then shortest our distance,
        # then maximize opponent distance.
        key = (sd <= od, -sd if sd <= od else 0, -od if sd <= od else (od - sd), sd, -r[0], -r[1])
        if best is None or key > best[0]:
            best = (key, r)
    target = best[1]

    tx, ty = target
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                candidates.append((nx, ny, dx, dy))
    if not candidates:
        return [0, 0]

    # Score each move: reduce distance to our target, and keep opponent far from their closest.
    best_move = None
    for nx, ny, dx, dy in candidates:
        d_self = man((nx, ny), (tx, ty))
        d_opp = man((ox, oy), opp_target)
        # If we step onto the target resource, heavily prioritize.
        step_reward = 1000 if (nx, ny) == (tx, ty) else 0
        # Mild bias to not step away from target.
        tie_bias = -d_self
        score = step_reward - d_self + 0.05 * d_opp + tie_bias * 0.001
        if best_move is None or score > best_move[0]:
            best_move = (score, dx, dy)

    return [int(best_move[1]), int(best_move[2])]
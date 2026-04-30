def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    opp = (ox, oy)
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) not in obstacles and (nx, ny) != opp:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    # Choose a target resource where we have positional advantage over opponent.
    if resources:
        best_adv = -10**9
        best_targets = []
        for r in resources:
            myd = dist((sx, sy), r)
            opd = dist(opp, r)
            adv = (opd - myd)  # higher means opponent is farther
            if adv > best_adv:
                best_adv = adv
                best_targets = [r]
            elif adv == best_adv:
                best_targets.append(r)
        # Deterministically pick among ties by smallest resource distance to me, then coordinates.
        target = min(best_targets, key=lambda r: (dist((sx, sy), r), r[0], r[1]))
    else:
        # No visible resources: head toward center to reduce distance variance.
        target = (w // 2, h // 2)

    # Score moves: gain by getting closer to target, deny opponent by reducing our advantage gap.
    cx, cy = w // 2, h // 2
    best = None
    best_score = -10**18
    for dx, dy, nx, ny in legal:
        myd = dist((nx, ny), target)
        oppd = dist(opp, target)

        # Encourage progress; discourage losing advantage; avoid getting too close to opponent.
        score = -myd * 4
        score += (oppd - myd) * 2

        # Obstacle-aware: prefer moves with more free adjacent space.
        free = 0
        for ddx, ddy in moves:
            tx, ty = nx + ddx, ny + ddy
            if inside(tx, ty) and (tx, ty) not in obstacles and (tx, ty) != opp:
                free += 1
        score += free * 0.15

        # Mild center control if no resources.
        if not resources:
            score += -dist((nx, ny), (cx, cy)) * 0.2

        # Deterministic tie-breaker: prefer staying directionally consistent toward target.
        score += -abs(nx - target[0]) * 0.01 - abs(ny - target[1]) * 0.01

        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]
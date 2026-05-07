def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(a, b):
        dx = abs(a[0] - b[0]); dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx = sx + dx; ny = sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                cand.append((dx, dy))
    if not cand:
        return [0, 0]

    # deterministic tie-break order
    cand.sort(key=lambda m: (m[0], m[1]))

    best_move = cand[0]
    best_score = -10**18
    for dx, dy in cand:
        nx = sx + dx; ny = sy + dy
        pos = (nx, ny)

        # If we move onto a resource, heavily prioritize that
        on_res = 1 if pos in set(resources) else 0

        my_best = 10**9
        op_best = 10**9
        for r in resources:
            myd = cheb(pos, r)
            opd = cheb((ox, oy), r)
            if myd < my_best:
                my_best = myd
            if opd < op_best:
                op_best = opd

        # Prefer moves that reduce our distance and also improve our advantage vs opponent
        score = 0
        score += 1000 * on_res
        score += -20 * my_best
        score += 8 * (op_best - my_best)

        # Small preference for heading towards center to avoid wall-sticking
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        score += -0.5 * (abs(nx - cx) + abs(ny - cy))

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
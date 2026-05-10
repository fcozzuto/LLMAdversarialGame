def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    scored = []
    for rx, ry in resources:
        my_d = cheb(sx, sy, rx, ry)
        op_d = cheb(ox, oy, rx, ry)
        # Prefer resources we can get no later than opponent; then maximize (op_d - my_d);
        # then prefer closer; then deterministically prefer smaller coordinates.
        feasible = 1 if my_d <= op_d else 0
        key = (feasible, op_d - my_d, -my_d, -rx, -ry)
        scored.append((key, rx, ry))
    scored.sort(key=lambda t: t[0], reverse=True)
    rx, ry = scored[0][1], scored[0][2]

    # Candidate moves: 8-neighborhood + stay, deterministic tie-breaking by fixed order.
    deltas = []
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            deltas.append((dx, dy))
    # Deterministic order: try diagonals and forward-ish first toward target
    # (reorder based on direction to target, but still deterministic).
    tx = 0 if rx == sx else (1 if rx > sx else -1)
    ty = 0 if ry == sy else (1 if ry > sy else -1)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    best = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        my_d2 = cheb(nx, ny, rx, ry)
        op_d2 = cheb(ox, oy, rx, ry)
        # Primary: reduce our distance to target; Secondary: improve relative advantage
        # (since opponent position may be changed in real play, we use static op_d).
        score = (-(my_d2), (op_d2 - my_d2), -abs(nx - rx) - abs(ny - ry), -dx*dx - dy*dy)
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]

    # Micro-avoid "getting stuck": if chosen move doesn't move closer, try a direct step toward target if legal.
    if cheb(sx, sy, rx, ry) <= cheb(sx + best[0], sy + best[1], rx, ry):
        candidates = [(tx, ty), (tx, 0), (0, ty), (tx, -ty), (0, 0)]
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            if in_bounds(nx, ny) and (nx, ny) not in obstacles:
                return [int(dx), int(dy)]
    return [int(best[0]), int(best[1])]
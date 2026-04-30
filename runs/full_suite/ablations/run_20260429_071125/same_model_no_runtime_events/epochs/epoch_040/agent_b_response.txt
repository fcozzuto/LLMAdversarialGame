def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def kdist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        # Deterministic: move toward center while avoiding obstacles
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            score = kdist(nx, ny, tx, ty)
            key = (score, nx, ny, dx, dy)
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1] if best else [0, 0]

    # Choose a target resource: prefer where we can arrive earlier than opponent, then closer overall
    best_target = None
    for tx, ty in resources:
        md = kdist(sx, sy, tx, ty)
        od = kdist(ox, oy, tx, ty)
        # Lower is better. Strongly favors resources we can reach sooner.
        key = (md - od, md, tx, ty)
        if best_target is None or key < best_target[0]:
            best_target = (key, (tx, ty))
    _, (tx, ty) = best_target

    # One-step lookahead: pick move that improves our reach while reducing opponent's advantage
    best_move = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd2 = kdist(nx, ny, tx, ty)
        od2 = kdist(ox, oy, tx, ty)
        # If tie, prefer reducing Manhattan-style component toward target and staying closer to center slightly
        center_bias = abs(nx - (w - 1) // 2) + abs(ny - (h - 1) // 2)
        md_now = kdist(sx, sy, tx, ty)
        improv = md_now - myd2
        score = (myd2 - od2, myd2, -improv, center_bias, nx, ny, dx, dy)
        if best_move is None or score < best_move[0]:
            best_move = (score, [dx, dy])

    return best_move[1] if best_move else [0, 0]
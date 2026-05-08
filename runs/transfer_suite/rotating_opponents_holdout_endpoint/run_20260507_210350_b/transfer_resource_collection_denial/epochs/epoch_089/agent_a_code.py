def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
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

    def king(a, b, c, d):
        return max(abs(a - c), abs(b - d))

    # Predict opponent's likely target: nearest (king distance) resource.
    opp_best = min(resources, key=lambda t: (king(ox, oy, t[0], t[1]), t[0], t[1]))
    # Choose a target that is good for us and not their most-likely one.
    # Objective: maximize (opp_dist - my_dist); secondarily, minimize my_dist.
    scored = []
    for t in resources:
        myd = king(sx, sy, t[0], t[1])
        opd = king(ox, oy, t[0], t[1])
        not_their = 1 if t != opp_best else 0
        val = (opd - myd, not_their, -myd, -abs(t[0]-t[1]))
        scored.append((val, t))
    _, target = max(scored, key=lambda x: x[0])

    tx, ty = target
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        myd = king(nx, ny, tx, ty)
        opd = king(ox, oy, tx, ty)
        # Prefer reducing our distance to target; also avoid letting opponent strictly get closer.
        val = (-(myd), 1 if king(ox, oy, tx, ty) >= myd else 0, -abs(nx - tx) - abs(ny - ty), dx, dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
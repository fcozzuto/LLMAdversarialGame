def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    w = int(observation["grid_width"]); h = int(observation["grid_height"])

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    # Pick a target resource: prefer ones we can reach earlier; otherwise closest.
    best = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Key: reach earlier, then closer, then deterministic tie.
        key = (0 if ds <= do else 1, ds, rx, ry) if ds <= do else (0 if do < ds else 1, do, rx, ry)
        if best is None or key < best[0]:
            best = (key, rx, ry, ds, do)
    _, tx, ty, _, _ = best

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if (tx, ty) in obstacles:
        # If target is blocked, redirect to closest unblocked resource.
        cand = [p for p in resources if tuple(p) not in obstacles]
        if cand:
            tx, ty = min(cand, key=lambda p: (man(sx, sy, p[0], p[1]), p[0], p[1]))

    def clamp(nx, ny):
        if nx < 0: nx = 0
        elif nx >= w: nx = w - 1
        if ny < 0: ny = 0
        elif ny >= h: ny = h - 1
        return nx, ny

    opp_moves = [(dx, dy) for dx, dy in moves]
    best_move = None
    best_score = None

    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)
        if (nx, ny) in obstacles:
            continue

        my_d = man(nx, ny, tx, ty)

        # Estimate opponent's best next distance to our target (resource denier response).
        op_best = 10**9
        for odx, ody in opp_moves:
            ox2, oy2 = clamp(ox + odx, oy + ody)
            if (ox2, oy2) in obstacles:
                continue
            op_best = min(op_best, man(ox2, oy2, tx, ty))

        # Score: maximize advantage; small preference for reducing own distance.
        # If opponent can get closer than us, penalize.
        score = (op_best - my_d, -my_d, -dx, -dy, nx, ny)

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]
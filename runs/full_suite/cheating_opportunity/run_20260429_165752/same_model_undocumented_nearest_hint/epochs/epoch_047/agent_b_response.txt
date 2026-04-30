def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        return [0, 0]

    # Target resources where we have a stronger relative claim than the opponent.
    best = None
    best_key = None
    for tx, ty in resources:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        rel = od - sd  # higher => we are closer than opponent
        tie = -(sd * 10 + (tx + ty) % 3)  # deterministic tie-break
        key = (rel, tie, -tx, -ty)
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best

    # Pick move that improves our distance and worsens opponent contest, while respecting obstacles.
    best_move = [0, 0]
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < W and 0 <= ny < H) or (nx, ny) in obstacles:
            continue
        ns = cheb(nx, ny, tx, ty)
        os = cheb(ox, oy, tx, ty)
        # Prefer reducing our distance to target; also slightly discourage stepping into cells that are too close to opponent.
        # (Opponent position is static for this move; this term still helps choose between equally good distance reductions.)
        dist_op_to_new = cheb(ox, oy, nx, ny)
        score = (-ns, os, dist_op_to_new, -(abs(dx) + abs(dy)), (nx + 2 * ny) % 2)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move
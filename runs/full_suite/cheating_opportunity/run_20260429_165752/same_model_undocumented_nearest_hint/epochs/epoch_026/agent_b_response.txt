def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
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
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = W // 2, H // 2

    # Determine best resource target by advantage (opponent farther than us).
    if resources:
        best_target = resources[0]
        best_val = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer big advantage; break ties by smaller self distance.
            val = (do - ds) * 1000 - ds
            if best_val is None or val > best_val:
                best_val = val
                best_target = (rx, ry)
        tx, ty = best_target
    else:
        tx, ty = cx, cy

    # Score moves: maximize reduction to target and denying opponent; avoid dangerous proximity.
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds2 = cheb(nx, ny, tx, ty)
        do2 = cheb(ox, oy, tx, ty)

        # Improvement toward target and keeping opponent behind.
        score = (cheb(sx, sy, tx, ty) - ds2) * 50 + (do2 - cheb(ox, oy, tx, ty)) * 5
        score += (do2 - ds2) * 80  # aim for resources where opponent can't catch as quickly

        # Mild avoidance: don't step into being too close to opponent unless it also improves target.
        dist_to_op = cheb(nx, ny, ox, oy)
        if dist_to_op <= 1:
            score -= 40
        elif dist_to_op == 2:
            score -= 10

        # Small center bias to avoid deadlocks when no clear resources.
        if not resources:
            score -= cheb(nx, ny, cx, cy) * 1

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
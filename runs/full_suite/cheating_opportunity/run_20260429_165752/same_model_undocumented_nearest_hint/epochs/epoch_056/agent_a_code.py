def choose_move(observation):
    W = int(observation.get("grid_width", 8))
    H = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [W - 1, H - 1])
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
    if not resources:
        resources = [(W // 2, H // 2)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = W // 2, H // 2

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Evaluate this move by the best "winning" resource target.
        # Prefer resources where we are closer than opponent; otherwise, avoid giving them advantage.
        val = 0
        local_best = -10**18
        for i, (tx, ty) in enumerate(resources):
            d_me = cheb(nx, ny, tx, ty)
            d_op = cheb(ox, oy, tx, ty)
            # Advantage term: larger when opponent is farther.
            adv = d_op - d_me
            # Primary: maximize advantage; Secondary: prioritize speed and less center bias if tied.
            score = adv * 1000 - d_me * 3
            if (tx, ty) == (cx, cy):
                score += 5
            # Deterministic tie-break using resource index.
            score -= i * 0.001
            if score > local_best:
                local_best = score

        val = local_best
        # Small deterrent if we move closer to opponent without improving advantage.
        d_op_now = cheb(nx, ny, ox, oy)
        val -= 0.2 * d_op_now

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
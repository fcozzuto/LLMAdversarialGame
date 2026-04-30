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
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            d_self = cheb(sx, sy, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # Prefer resources where we are closer; also prefer those with larger lead over opponent.
            key = (-(d_self), -(d_opp - d_self), rx + 10 * ry)
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best
    else:
        tx, ty = (W - 1) // 2, (H - 1) // 2

    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d_self = cheb(nx, ny, tx, ty)
        d_curr = cheb(sx, sy, tx, ty)
        d_opp_after = cheb(ox, oy, tx, ty)

        # Score: make progress to target, increase advantage over opponent, avoid stepping away.
        progress = d_curr - d_self
        advantage = (d_opp_after - d_self)
        center_bias = -cheb(nx, ny, (W - 1) // 2, (H - 1) // 2) * 0.01
        score = (progress * 10, advantage, center_bias, -(abs(dx) + abs(dy)))

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move
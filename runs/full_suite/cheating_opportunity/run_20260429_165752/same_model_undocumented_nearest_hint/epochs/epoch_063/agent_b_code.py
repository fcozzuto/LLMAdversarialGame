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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles

    # Target selection: maximize winning chance to reach resources first; deterministic tie-breakers.
    if resources:
        best = None
        bestv = None
        for tx, ty in resources:
            d_me = cheb(sx, sy, tx, ty)
            d_op = cheb(ox, oy, tx, ty)
            # Big reward for being closer; slight preference for nearer resources and later disruption of opponent.
            v = (d_op - d_me) * 10000 - d_me * 10 + (d_me - d_op)
            if bestv is None or v > bestv or (v == bestv and (d_me, -d_op, tx, ty) < best):
                bestv = v
                best = (d_me, -d_op, tx, ty)
        tx, ty = best[2], best[3]
    else:
        # No visible resources: drift to center-ish while keeping away from opponent.
        tx, ty = W // 2, H // 2

    # Move selection: prioritize reducing distance to target; avoid moving into opponent pressure.
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d_new = cheb(nx, ny, tx, ty)
        d_old = cheb(sx, sy, tx, ty)
        d_op_new = cheb(nx, ny, ox, oy)
        d_op_old = cheb(sx, sy, ox, oy)

        # Score: improve target distance first; if tied, maximize opponent distance; if still tied, deterministic order by dx,dy.
        score = (-(d_new - d_old), -d_new, d_op_new, -abs(dx) - abs(dy))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
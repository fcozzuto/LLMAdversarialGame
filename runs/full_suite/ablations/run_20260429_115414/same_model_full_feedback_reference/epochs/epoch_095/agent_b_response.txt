def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    def legal(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if legal(x, y):
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not legal(sx, sy):
        for dx, dy in [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
            if legal(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    if resources:
        best = None
        # Prefer resources we can reach sooner than the opponent; then closest.
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            score = (do - ds, -ds, rx, ry)  # maximize (do-ds), then minimize ds
            if best is None or score > best[0]:
                best = (score, (rx, ry))
        tx, ty = best[1]
    else:
        # No visible resources: drift toward opponent corner-adjacent or safe center if blocked.
        tx, ty = (W - 1, H - 1)
        if not legal(tx, ty):
            for t in [(W // 2, H // 2), (W // 2, H - 1), (W - 1, H // 2)]:
                if legal(t[0], t[1]):
                    tx, ty = t
                    break

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (None, None)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d_to_target = cheb(nx, ny, tx, ty)
        d_to_opp = cheb(nx, ny, ox, oy)
        # Move toward target; keep some distance from opponent if similarly good.
        val = (-(d_to_target), d_to_opp, -abs((tx - nx)) - abs((ty - ny)))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    if best_move[0] is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]
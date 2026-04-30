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

    def ok(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (W - 1) / 2.0, (H - 1) / 2.0

    if resources:
        best = None
        best_val = -10**18
        for tx, ty in resources:
            myd = cheb(sx, sy, tx, ty)
            opd = cheb(ox, oy, tx, ty)
            # Prefer targets where we are closer; tie-break by closeness and centrality
            val = (opd - myd) * 10 - myd - 0.05 * (abs(tx - cx) + abs(ty - cy))
            if val > best_val:
                best_val = val
                best = (tx, ty)
        tx, ty = best

        best_move = (0, 0)
        best_score = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            myd = cheb(nx, ny, tx, ty)
            opd_now = cheb(ox, oy, tx, ty)
            # Encourage progress; also keep some distance from opponent (soft)
            score = -myd * 10 + (opd_now - myd) * 3 + 0.2 * cheb(nx, ny, ox, oy) - 0.001 * (abs(nx - cx) + abs(ny - cy))
            if score > best_score:
                best_score = score
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No visible resources: move toward center while not stepping into obstacles
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        score = -(abs(nx - cx) + abs(ny - cy)) - 0.05 * cheb(nx, ny, ox, oy)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]
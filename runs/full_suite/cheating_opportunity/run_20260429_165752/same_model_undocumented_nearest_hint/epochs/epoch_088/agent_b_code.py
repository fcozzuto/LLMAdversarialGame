def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
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

    def inside(nx, ny):
        return 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def best_resource():
        if not resources:
            return None
        best = None
        best_score = None
        for rx, ry in resources:
            d_self = cheb(sx, sy, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            score = (d_self - d_opp) * 10 + d_self
            if best is None or score < best_score:
                best = (rx, ry)
                best_score = score
        return best

    target = best_resource()
    if target is None:
        tx, ty = (W - 1) // 2, (H - 1) // 2
    else:
        tx, ty = target

    best_move = None
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d_to = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, ox, oy)
        if resources and target is not None:
            d_self_now = cheb(nx, ny, tx, ty)
            d_opp_now = cheb(ox, oy, tx, ty)
            val = -(d_self_now) * 100 + d_opp * 3 - d_opp_now
        else:
            val = -d_to * 50 + d_opp * 5
        if best_move is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    if best_move is None:
        if inside(sx, sy):
            return [0, 0]
        for dx, dy in moves:
            if inside(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]
    return best_move
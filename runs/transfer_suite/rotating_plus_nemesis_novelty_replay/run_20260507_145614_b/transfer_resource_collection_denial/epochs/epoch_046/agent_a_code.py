def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        return [dx, dy]

    for r in resources:
        if sx == r[0] and sy == r[1]:
            return [0, 0]

    best_r = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach sooner; break ties toward closer cells
        key = (opd - myd, -myd, -((rx + ry) % 7))
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    for dxi, dyi in moves:
        nx, ny = sx + dxi, sy + dyi
        if not valid(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # Also slightly prefer moves that increase distance between opponent and our chosen target
        score = 0
        score += (opd - myd) * 200
        score += (100 - myd) * 3
        if (nx, ny) == (tx, ty):
            score += 1000000
        # Small tie-break toward moving toward target direction
        score += -cheb(nx, ny, sx, sy) * 0.01
        if score > best_score:
            best_score = score
            best_move = (dxi, dyi)

    return [int(best_move[0]), int(best_move[1])]
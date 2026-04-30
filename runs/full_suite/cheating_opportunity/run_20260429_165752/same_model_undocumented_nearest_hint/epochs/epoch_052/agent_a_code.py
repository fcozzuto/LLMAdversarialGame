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

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_t = None
    best_s = -10**18
    for tx, ty in resources:
        myd = cheb(sx, sy, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        lead = opd - myd  # positive = we are closer
        near = 1 if myd <= 1 else 0
        # Favor contested advantage; penalize resources where opponent is strictly closer.
        score = lead * 100 + near * 20 - myd + (1 if opd > myd else -2)
        if score > best_s:
            best_s = score
            best_t = (tx, ty)

    tx, ty = best_t
    curd = cheb(sx, sy, tx, ty)
    best_m = (0, 0)
    best_m_s = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # Heuristic: maximize improvement toward target; if opponent is closer, still try to stall by denying proximity.
        improvement = curd - myd
        adj_opp = 1 if cheb(nx, ny, ox, oy) <= 1 else 0
        # If opponent is currently closer to the target, prefer stepping that increases opponent-target distance (proxy via our safety).
        safety = 0
        if opd < myd:
            safety = (cheb(ox, oy, tx, ty) - cheb(nx, ny, tx, ty))  # tends to be negative, we negate via formula below
        s = improvement * 50 - myd * 3 + (1 if myd <= curd else -2) - adj_opp * 25 + safety * 2
        if s > best_m_s or (s == best_m_s and (dx, dy) == (0, 0)):
            best_m_s = s
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]
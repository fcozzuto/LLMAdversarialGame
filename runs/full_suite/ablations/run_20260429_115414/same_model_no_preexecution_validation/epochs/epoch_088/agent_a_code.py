def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Target: maximize how much closer we are than opponent; deterministic tie-breaks.
    best = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer immediate opportunities; also prefer closer overall in tie.
        key = (od - sd, -sd, -cheb(ox, oy, rx, ry), rx, ry)
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    # Two-step greedy lookahead to avoid obstacle-walls; deterministic neighbor ordering.
    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # Lookahead one step: choose best continuation distance, then compare opponent impact.
        best_cont = None
        for ddx, ddy in dirs:
            nnx, nny = nx + ddx, ny + ddy
            if not ok(nnx, nny):
                continue
            d1 = cheb(nnx, nny, tx, ty)
            # discourage moving closer to opponent when contested
            d_op = cheb(nnx, nny, ox, oy)
            k = (d1, -d_op, nnx, nny)
            if best_cont is None or k < best_cont:
                best_cont = k
        if best_cont is None:
            continue
        cont_d = best_cont[0]
        # Primary: minimize our distance to target after lookahead; Secondary: keep away from opponent.
        d_now = cheb(nx, ny, tx, ty)
        k2 = (cont_d, d_now, -cheb(nx, ny, ox, oy), dx, dy)
        if best_move is None or k2 < best_move[0]:
            best_move = (k2, [dx, dy])

    if best_move is None:
        return [0, 0]
    return best_move[1]
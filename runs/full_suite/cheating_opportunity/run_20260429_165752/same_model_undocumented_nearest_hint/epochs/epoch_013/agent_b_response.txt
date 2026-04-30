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

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def eval_pos(x, y, tx, ty):
        ds = cheb(x, y, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # Prefer increasing advantage now, and break ties by getting closer.
        return (do - ds) * 10 - ds

    if resources:
        best = None
        best_adv = -10**9
        for rx, ry in resources:
            adv = cheb(ox, oy, rx, ry) - cheb(sx, sy, rx, ry)
            if adv > best_adv:
                best_adv = adv
                best = (rx, ry)
        tx, ty = best
        best_move = (0, 0)
        best_val = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            val = eval_pos(nx, ny, tx, ty)
            # Small deterministic bias to avoid oscillation.
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No resources: drift toward center while keeping legal move.
    cx, cy = (W - 1) / 2.0, (H - 1) / 2.0
    best_move = (0, 0)
    best_val = 10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
        if d < best_val:
            best_val = d
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]
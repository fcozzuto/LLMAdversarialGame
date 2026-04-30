def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles

    if not resources:
        tx, ty = W // 2, H // 2
    else:
        tx, ty = resources[0]

    best = (0, 0)
    best_val = None

    # deterministic tie-break by move order
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        if resources:
            # choose closest resource for evaluation (still deterministic)
            dmin = None
            for rx, ry in resources:
                d = cheb(nx, ny, rx, ry)
                if dmin is None or d < dmin:
                    dmin = d
            val = -dmin
        else:
            val = -cheb(nx, ny, tx, ty)
        if best_val is None or val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]
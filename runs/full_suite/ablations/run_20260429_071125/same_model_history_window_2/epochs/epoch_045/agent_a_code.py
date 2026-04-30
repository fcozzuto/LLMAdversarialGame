def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) == 2:
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

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Pick target that we can reach sooner than opponent (maximize (oppDist - selfDist))
    best_t = None
    best_k = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        k = (od - sd, -sd, -rx, -ry)
        if best_k is None or k > best_k:
            best_k = k
            best_t = (rx, ry)

    tx, ty = best_t
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # One-step lookahead: choose legal move maximizing advantage after move; also avoid moving next to opponent
    best_m = (0, 0)
    best_v = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        sd = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # Prefer immediate advantage increase; penalize adjacency/contact with opponent
        adj = (abs(nx - ox) <= 1 and abs(ny - oy) <= 1)
        v = (od - sd, -sd, 0 if not adj else -1, -dx, -dy)
        if best_v is None or v > best_v:
            best_v = v
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]
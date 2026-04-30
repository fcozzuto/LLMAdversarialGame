def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    if not resources:
        # retreat toward center while keeping away from opponent
        cx, cy = (W - 1) // 2, (H - 1) // 2
        best = (0, 0)
        bestv = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): 
                continue
            v = (cheb(nx, ny, cx, cy), -cheb(nx, ny, ox, oy), nx, ny)
            if bestv is None or v < bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Choose a target with two-level priority: closest to us, and not too close to opponent
    best_t = None
    best_key = None
    for rx, ry in resources:
        du = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        key = (du, -(do - du), rx, ry)  # prefer small du, and resources where we are relatively closer
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t

    # Evaluate immediate moves: progress to target, increase distance from opponent, and avoid stepping adjacent to obstacles
    def obstacle_risk(nx, ny):
        r = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (nx + dx, ny + dy) in obstacles:
                    r += 1
        return r

    best = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        prog = cheb(nx, ny, tx, ty)
        dist_opp = cheb(nx, ny, ox, oy)
        # If tied on progress, strongly prefer moves that increase separation from opponent
        val = (prog, -dist_opp, obstacle_risk(nx, ny), nx, ny)
        if best_val is None or val < best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]
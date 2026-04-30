def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
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
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (W - 1) / 2.0, (H - 1) / 2.0

    def target_score(tx, ty):
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        closer = (do - ds)  # positive if we are closer
        # slight bias toward nearer targets to finish earlier and toward center
        center_bias = cheb(tx, ty, cx, cy) * 0.01
        return closer * 10.0 - ds * 0.2 - center_bias

    best_t = None
    best_v = -10**18
    for tx, ty in resources:
        v = target_score(tx, ty)
        if v > best_v:
            best_v = v
            best_t = (tx, ty)

    tx, ty = best_t if best_t is not None else (int(cx), int(cy))
    # Greedy step toward target with deterministic tie-break using fixed move order
    best_m = (0, 0)
    best_d = 10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        # secondary: avoid moving closer to opponent when equally good for our target
        do = cheb(nx, ny, ox, oy)
        key = (d, do)
        best_key = (best_d, cheb(sx + best_m[0], sy + best_m[1], ox, oy))
        if key < best_key:
            best_d = d
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]
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

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def mobility(x, y):
        c = 0
        for ddx, ddy in dirs:
            nx, ny = x + ddx, y + ddy
            if legal(nx, ny):
                c += 1
        return c

    cx, cy = W // 2, H // 2
    if not resources:
        best = [0, 0]
        best_score = -10**9
        for ddx, ddy in sorted(dirs):
            nx, ny = sx + ddx, sy + ddy
            if not legal(nx, ny):
                continue
            score = -cheb(nx, ny, cx, cy) + 0.1 * mobility(nx, ny)
            if score > best_score:
                best_score = score
                best = [ddx, ddy]
        return best

    best = [0, 0]
    best_score = -10**18
    ordered_dirs = sorted(dirs)
    for ddx, ddy in ordered_dirs:
        nx, ny = sx + ddx, sy + ddy
        if not legal(nx, ny):
            continue
        m = mobility(nx, ny)
        local_best = -10**18
        for tx, ty in resources:
            self_d = cheb(nx, ny, tx, ty)
            opp_d = cheb(ox, oy, tx, ty)
            win_bias = 6 if self_d < opp_d else (-2 if self_d > opp_d else 1)
            val = (opp_d - self_d) * 10 - self_d + win_bias
            if self_d == 0:
                val += 50
            # small preference for staying on "active" side of the grid
            val += 0.05 * (m - 4)
            if val > local_best:
                local_best = val
        if local_best > best_score:
            best_score = local_best
            best = [ddx, ddy]
    return best
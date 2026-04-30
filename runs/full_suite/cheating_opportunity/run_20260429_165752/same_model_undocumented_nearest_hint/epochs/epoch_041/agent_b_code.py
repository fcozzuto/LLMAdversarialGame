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
    resources = sorted(set(resources))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    if not resources:
        tx, ty = (W - 1) if ox <= (W - 1) // 2 else 0, (H - 1) if oy <= (H - 1) // 2 else 0
        best_dir = (0, 0)
        best_val = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            v = -cheb(nx, ny, (W - 1 + 0) // 2, (H - 1 + 0) // 2) - 0.3 * cheb(nx, ny, ox, oy)
            if cheb(nx, ny, tx, ty) == 0:
                v += 1000
            if v > best_val:
                best_val = v
                best_dir = (dx, dy)
        return [int(best_dir[0]), int(best_dir[1])]

    best_resource = min(resources, key=lambda t: (cheb(sx, sy, t[0], t[1]), t[0], t[1]))
    best_dir = (0, 0)
    best_val = -10**18

    # Prefer moves that secure a resource sooner than opponent; small bias to closest-to-us.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        val = -cheb(nx, ny, best_resource[0], best_resource[1]) * 0.05
        min_margin = 10**9
        for rx, ry in resources:
            d_s = cheb(nx, ny, rx, ry)
            d_o = cheb(ox, oy, rx, ry)
            margin = d_o - d_s
            if d_s == 0:
                margin += 1000
            if margin < min_margin:
                min_margin = margin
        # Make the move that maximizes the worst-case margin across visible resources.
        val += min_margin
        # Secondary tie-break: reduce distance to opponent resources that are closest to us.
        if resources:
            val += -cheb(nx, ny, resources[0][0], resources[0][1]) * 0.01
        if val > best_val:
            best_val = val
            best_dir = (dx, dy)

    return [int(best_dir[0]), int(best_dir[1])]
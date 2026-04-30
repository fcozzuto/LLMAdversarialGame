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

    def best_move_for_target(tx, ty):
        best_val = -10**18
        best = (0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d_self = cheb(nx, ny, tx, ty)
            d_opp = cheb(nx, ny, ox, oy)
            # Prefer closing on target we are more likely to secure, while not walking too close to opponent.
            val = (-d_self * 3) + (d_opp * 0.15)
            if val > best_val or (val == best_val and (dx, dy) < best):
                best_val = val
                best = (dx, dy)
        return [best[0], best[1]]

    if resources:
        # Target resource where we are relatively closer than opponent (materially different from pure nearest).
        target = None
        best_key = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            key = (do - ds, -ds, rx, ry)  # maximize advantage, then prefer smaller ds deterministically
            if best_key is None or key > best_key:
                best_key = key
                target = (rx, ry)
        return best_move_for_target(target[0], target[1])

    # No resources: maximize distance from opponent safely.
    best_val = -10**18
    best = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        val = cheb(nx, ny, ox, oy)
        if val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)
    return [best[0], best[1]]
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

    def in_ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def near_obst(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    c += 1
        return c

    # Choose a target we can reach no worse than opponent, else least bad.
    best = None
    best_key = None
    for tx, ty in resources:
        d1 = cheb(sx, sy, tx, ty)
        d2 = cheb(ox, oy, tx, ty)
        key = (0, d1) if d1 <= d2 else (1, d1 - d2, d1)
        if best_key is None or key < best_key:
            best_key = key
            best = (tx, ty)
    tx, ty = best

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cur_d = cheb(sx, sy, tx, ty)

    best_move = (0, 0)
    best_val = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_ok(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        # Prefer progress to target; avoid obstacles; slight preference toward staying closer to target.
        val = 100 * (cur_d - nd) - 3 * near_obst(nx, ny) - (nd * 1)
        # If near tie, bias toward not drifting away from center.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        dist_center = abs(nx - cx) + abs(ny - cy)
        val -= int(dist_center)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    resources = observation.get("resources") or []
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        return [0, 0]

    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Choose target resource deterministically by best advantage from this next position
        local_best = None
        for r in resources:
            if not r or len(r) < 2:
                continue
            tx = int(r[0]); ty = int(r[1])
            if not (0 <= tx < w and 0 <= ty < h):
                continue
            ds = man(nx, ny, tx, ty)
            do = man(ox, oy, tx, ty)
            # Prefer resources where we arrive no later than opponent, then larger positive margin, then smaller ds
            val = (0 if ds <= do else 1, -(do - ds), ds, tx, ty)
            if local_best is None or val < local_best[0]:
                local_best = (val, ds, do)
        if local_best is None:
            continue
        # Evaluate move by its chosen target; slightly prefer staying closer to center-ish to avoid deadlocks
        margin = -local_best[0][1]
        center_bias = abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0)
        move_val = (local_best[0], -margin, center_bias, dx, dy)
        if best_val is None or move_val < best_val:
            best_val = move_val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
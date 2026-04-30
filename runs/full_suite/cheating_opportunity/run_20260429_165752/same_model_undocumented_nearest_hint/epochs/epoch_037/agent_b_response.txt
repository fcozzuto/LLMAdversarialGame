def choose_move(observation):
    W = int(observation.get("grid_width", 8))
    H = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [W - 1, H - 1]) or [W - 1, H - 1]
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

    def ok(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def danger(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    c += 1
        return c

    def resource_priority(x, y):
        md = cheb(sx, sy, x, y)
        od = cheb(ox, oy, x, y)
        # Material shift vs last epoch policy: explicitly prioritize contesting losses (od < md)
        # and reduce path clutter by penalizing obstacle-adjacent targets.
        return (od - md, md, danger(x, y))

    # Choose target: either we can win quickly, or we contest a resource where opponent is closer.
    target = None
    if resources:
        best = None
        for x, y in resources:
            pr = resource_priority(x, y)
            if best is None or pr < best:
                best = pr
                target = (x, y)
    else:
        target = (ox, oy)  # fallback: drift to reduce opponent scoring

    tx, ty = target
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # If target is already adjacent, step toward it while staying away from obstacle pockets.
    best_move = (0, 0)
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d1 = cheb(nx, ny, tx, ty)
        # Secondary objective: avoid moves that let opponent gain too much toward same target
        # (use one-step opponent projection deterministically).
        dop = cheb(ox, oy, tx, ty)
        # Bias away from staying if a better approach exists.
        stay_pen = 1 if dx == 0 and dy == 0 else 0
        key = (d1, stay_pen, danger(nx, ny), dop)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
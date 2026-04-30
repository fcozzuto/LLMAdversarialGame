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
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Score candidate resources by distance advantage; tie-break by closeness to me, then fixed order.
    best = None
    best_score = None
    ordered = sorted(resources, key=lambda t: (t[1], t[0]))
    for i, (rx, ry) in enumerate(ordered):
        d_me = cheb(sx, sy, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        adv = d_op - d_me  # positive means I'm closer
        # Encourage lower absolute time; discourage far-away races.
        score = (adv, -d_me, -i)
        if best_score is None or score > best_score:
            best_score = score
            best = (rx, ry)

    tx, ty = best

    # Choose best one-step move to reduce distance to target; if tied, move to increase advantage.
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d_to = cheb(nx, ny, tx, ty)
        d_me_now = cheb(nx, ny, tx, ty)
        d_op_to = cheb(ox, oy, tx, ty)
        adv_now = d_op_to - d_me_now
        # Multi-objective: minimize distance to target, maximize advantage, and avoid stepping too close to obstacles (lightly).
        # Obstacle proximity penalty (deterministic small weight).
        prox = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                xx, yy = nx + ax, ny + ay
                if (xx, yy) in obstacles:
                    prox += 1
        val = (-d_to, adv_now, -prox, dx, dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [w - 1, h - 1]) or [w - 1, h - 1]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def obs_adj(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    c += 1
        return c

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        # Fallback: move away from nearby obstacles, otherwise toward center.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            score = 10 * obs_adj(nx, ny) + cheb(nx, ny, cx, cy)
            if best is None or score < best[0]:
                best = (score, dx, dy)
        if best is None:
            return [0, 0]
        return [best[1], best[2]]

    # Pick best target with a deterministic contest bias, then choose the best immediate step.
    best_target = None
    best_tscore = None
    for tx, ty in resources:
        d_self = cheb(sx, sy, tx, ty)
        d_opp = cheb(ox, oy, tx, ty)
        # Lower is better: prefer closer to us; if tie, prefer where we are relatively closer.
        tscore = d_self - 0.7 * d_opp
        if best_tscore is None or tscore < best_tscore:
            best_tscore = tscore
            best_target = (tx, ty)
    tx, ty = best_target

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Prefer collecting: if moving onto resource, strongly prefer.
        immediate_resource = 1 if (nx, ny) in resources else 0
        dist_to_target = cheb(nx, ny, tx, ty)
        dist_to_opp = cheb(ox, oy, tx, ty)
        # Obstacle aversion for next step survival.
        score = (-1000 * immediate_resource) + 5 * obs_adj(nx, ny) + 1.2 * dist_to_target - 0.2 * dist_to_opp
        if best is None or score < best[0]:
            best = (score, dx, dy)

    if best is None:
        return [0, 0]
    return [best[1], best[2]]
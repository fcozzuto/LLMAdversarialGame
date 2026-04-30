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

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if resources:
        target = min(resources, key=lambda r: (cheb(sx, sy, r[0], r[1]), r[0], r[1]))
        tx, ty = target
    else:
        tx, ty = (w // 2 + (1 if sx < ox else -1)), (h // 2 + (1 if sy < oy else -1))
        tx = 0 if tx < 0 else w - 1 if tx >= w else tx
        ty = 0 if ty < 0 else h - 1 if ty >= h else ty

    best = None
    best_score = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_to_target = cheb(nx, ny, tx, ty)
        d_to_op = cheb(nx, ny, ox, oy)
        on_resource = 1 if (nx, ny) in set(resources) else 0
        # Prefer collecting immediately, then reducing distance to target, and avoid moving toward opponent too much.
        score = on_resource * 1000 - d_to_target * 10 + d_to_op * 1
        if best is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]
def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        tx, ty = None, None
        best = 10**18
        for x, y in resources:
            d = cheb(sx, sy, x, y)
            if d < best or (d == best and (x, y) < (tx, ty)):
                best = d
                tx, ty = x, y
        if tx is None:
            tx, ty = (w - 1) // 2, (h - 1) // 2

    prefer_avoid = (man(ox, oy, sx, sy) <= 2)

    best_move = (0, 0)
    best_val = -10**30
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_res = cheb(nx, ny, tx, ty)
        d_op = cheb(nx, ny, ox, oy)
        # Encourage grabbing resources; discourage tight opponent proximity.
        val = -d_res * 3.0 - man(nx, ny, tx, ty) * 0.15
        val += d_op * (0.9 if prefer_avoid else 0.25)
        # If no resources exist on immediate vicinity, slightly center.
        centerx, centery = (w - 1) / 2.0, (h - 1) / 2.0
        val -= (abs(nx - centerx) + abs(ny - centery)) * 0.02
        # If stepping onto an available resource, huge bonus (captured next).
        if (nx, ny) in resources:
            val += 1000.0
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
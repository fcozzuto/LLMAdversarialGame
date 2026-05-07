def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if inb(bx, by):
                obstacles.add((bx, by))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry) and (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    best_adv = None
    tx = ty = resources[0][0], resources[0][1]
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        adv = opd - myd
        cand = (adv, -myd, rx, ry)
        if best_adv is None or cand > best_adv:
            best_adv = cand
            tx, ty = rx, ry

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        myd2 = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        adv2 = opd - myd2
        # small deterministic tiebreak: prefer moves that head toward target
        head = (1 if (tx - nx) == 0 else 0, 1 if (ty - ny) == 0 else 0)
        val = (adv2, -myd2, -head[0], -head[1], dx, dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
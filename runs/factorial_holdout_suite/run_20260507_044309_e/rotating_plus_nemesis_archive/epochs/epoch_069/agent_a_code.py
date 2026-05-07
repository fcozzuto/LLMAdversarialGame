def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if inb(bx, by):
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry) and (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    best = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        cand = (opd - myd, -myd, rx, ry)
        if best is None or cand > best:
            best = cand
    tx, ty = best[2], best[3]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = None
    curd = cheb(sx, sy, tx, ty)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nd = cheb(nx, ny, tx, ty)
        opd_next = cheb(ox, oy, tx, ty)
        adv = opd_next - nd
        cand = (nd < curd, adv, -nd, -abs(nx - tx) - abs(ny - ty), dx, dy)
        if best_move is None or cand > best_move:
            best_move = cand

    if best_move is not None:
        return [int(best_move[4]), int(best_move[5])]

    # Fallback: any legal move that doesn't step into obstacles
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            return [int(dx), int(dy)]
    return [0, 0]
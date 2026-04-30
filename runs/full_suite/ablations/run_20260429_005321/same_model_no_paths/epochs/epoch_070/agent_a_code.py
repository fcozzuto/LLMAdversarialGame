def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y):
                resources.append((x, y))

    if resources:
        def cheb(ax, ay, bx, by):
            dx = ax - bx
            if dx < 0: dx = -dx
            dy = ay - by
            if dy < 0: dy = -dy
            return dx if dx > dy else dy
        target = min(resources, key=lambda t: (cheb(sx, sy, t[0], t[1]), t[0], t[1]))
        tx, ty = target
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best_move = [0, 0]
    best_val = -10**18
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if resources:
                d = abs(nx - tx)
                if (nd := abs(ny - ty)) > d:
                    d = nd
                score = -d
                od = abs(nx - ox)
                if (od2 := abs(ny - oy)) > od:
                    od = od2
                score += 0.2 * od
            else:
                score = -max(abs(nx - tx), abs(ny - ty))
            if score > best_val:
                best_val = score
                best_move = [dx, dy]

    if best_move == [0, 0]:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if inb(sx + dx, sy + dy):
                    return [dx, dy]
        return [0, 0]
    return best_move
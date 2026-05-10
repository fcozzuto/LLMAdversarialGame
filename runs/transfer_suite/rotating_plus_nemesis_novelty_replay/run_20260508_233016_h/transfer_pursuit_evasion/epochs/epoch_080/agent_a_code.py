def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles") or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resources = observation.get("resources") or []
    targets = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                targets.append((rx, ry))
    if not targets:
        targets = [(w//2, h//2), (0, 0), (w-1, 0), (0, h-1), (w-1, h-1)]

    tx, ty = min(targets, key=lambda t: cheb(sx, sy, t[0], t[1]))
    best = (10**9, 10**9, 10**9)
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dres = cheb(nx, ny, tx, ty)
        dopp = cheb(nx, ny, ox, oy)
        corner_bias = min(nx, ny, w - 1 - nx, h - 1 - ny)
        # Prefer smaller resource distance, then staying away from opponent, then moving toward corners
        key = (dres, -dopp, -corner_bias)
        if key < best:
            best = key
            best_move = [dx, dy]

    return best_move
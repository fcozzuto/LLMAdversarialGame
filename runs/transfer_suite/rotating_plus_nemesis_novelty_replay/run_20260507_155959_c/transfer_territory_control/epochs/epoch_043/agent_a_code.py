def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    resources = observation.get("resources") or []
    best_tx = ox
    best_ty = oy
    if resources:
        bestd = None
        for r in resources:
            if r is None or len(r) < 2:
                continue
            tx, ty = int(r[0]), int(r[1])
            if not inb(tx, ty) or blocked(tx, ty):
                continue
            d = manh(sx, sy, tx, ty)
            if bestd is None or d < bestd or (d == bestd and (tx, ty) < (best_tx, best_ty)):
                bestd = d
                best_tx, best_ty = tx, ty

    target_is_opponent = not resources

    move_order = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            move_order.append((dx, dy))
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in move_order:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue

        score = 0
        if target_is_opponent:
            score -= manh(nx, ny, ox, oy) * 10
            # Slight preference to not step onto opponent (if it exists on-grid)
            if nx == ox and ny == oy:
                score -= 100000
        else:
            score -= manh(nx, ny, best_tx, best_ty) * 10
            score -= manh(nx, ny, ox, oy)

        # Deterministic micro-boost: keep moving in same general direction
        if dx != 0 or dy != 0:
            score += (dx + 1) * 0.01 + (dy + 1) * 0.001

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        return [0, 0]
    return [dx, dy]
def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                resources.append((rx, ry))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    options = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_score = -10**18

    def cell_ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    if not resources:
        tx, ty = w // 2, h // 2
        for dx, dy in options:
            nx, ny = sx + dx, sy + dy
            if not cell_ok(nx, ny):
                nx, ny = sx, sy
            d = cheb(nx, ny, tx, ty)
            sc = -d * 10 + (nx - sx) * 0.01 + (ny - sy) * 0.02
            if sc > best_score:
                best_score = sc
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    for dx, dy in options:
        nx, ny = sx + dx, sy + dy
        if not cell_ok(nx, ny):
            nx, ny = sx, sy
        # Target scoring: prioritize resources where opponent is relatively farther.
        best_for_move = -10**18
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # adv > 0 means we are closer than opponent
            adv = od - sd
            # Slightly prefer closer resources to reduce time-to-first-pick
            val = adv * 60 - sd * 5 - (abs(rx - nx) + abs(ry - ny)) * 0.5
            if val > best_for_move:
                best_for_move = val
        # Deterministic tie-break: favor moves with smaller dx, then smaller dy, then toward increasing x/y.
        tie = -abs(dx) * 0.001 - abs(dy) * 0.0002 + (nx * 1e-6) + (ny * 2e-6)
        sc = best_for_move + tie
        if sc > best_score:
            best_score = sc
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]
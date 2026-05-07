def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    moves = [(-1, 0), (0, -1), (1, 0), (0, 1), (0, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    ti = int(observation.get("turn_index") or 0)
    if ti % 2 == 1:
        moves = [m for m in moves if m != (0, 0)] + [(0, 0)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    oppd = cheb(sx, sy, ox, oy)
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        mind = 10**9
        for rx, ry in resources:
            d = cheb(nx, ny, rx, ry)
            if d < mind:
                mind = d

        # Prefer approaching closest resource; when opponent is near, add separation.
        val = -(mind * 10)
        if oppd <= 2:
            sep = cheb(nx, ny, ox, oy)
            val += sep * 6
        elif oppd <= 4:
            sep = cheb(nx, ny, ox, oy)
            val += sep * 2
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
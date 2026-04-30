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

    resources = set()
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                resources.add((rx, ry))

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0:
            dx = -dx
        dy = a[1] - b[1]
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal_moves = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if legal(nx, ny):
            legal_moves.append((nx, ny, dx, dy))
    if not legal_moves:
        return [0, 0]

    if resources:
        target = min(resources, key=lambda p: (cheb((sx, sy), p), p[0], p[1]))
    else:
        target = (ox, oy)

    best = None
    best_score = -10**18
    for nx, ny, dx, dy in legal_moves:
        pos = (nx, ny)
        on_res = 1 if pos in resources else 0
        d_us = cheb(pos, target)
        d_opp = cheb((ox, oy), target)

        # Encourage reaching the target, and discourage giving the opponent an advantage.
        d_opp_from_us = cheb(pos, (ox, oy))
        score = on_res * 100000 - d_us * 10 + d_opp * 2 - d_opp_from_us * 0.3

        if best is None or score > best_score:
            best_score = score
            best = (dx, dy)
        elif score == best_score:
            if (dx, dy) < best:
                best = (dx, dy)

    return [int(best[0]), int(best[1])]
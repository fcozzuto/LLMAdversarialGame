def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if ok(rx, ry):
                resources.append((rx, ry))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    if resources:
        best = None
        best_move = (0, 0)
        # Deterministic tie-break order by preferring smaller dx, then dy.
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            move_best = None
            for rx, ry in resources:
                dself = cheb(nx, ny, rx, ry)
                dobb = cheb(ox, oy, rx, ry)
                # Prefer targets where we can beat/tie opponent; slightly prefer nearer and safer positions.
                score = (dobb - dself) * 100 - dself - 0.01 * cheb(nx, ny, w // 2, h // 2)
                if move_best is None or score > move_best:
                    move_best = score
            if best is None or move_best > best or (move_best == best and (dx, dy) < best_move):
                best = move_best
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No resources: move toward center while keeping distance from opponent.
    cx, cy = w // 2, h // 2
    best_score = None
    best_move = (0, 0)
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        score = -cheb(nx, ny, cx, cy) + 0.1 * cheb(nx, ny, ox, oy)
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]
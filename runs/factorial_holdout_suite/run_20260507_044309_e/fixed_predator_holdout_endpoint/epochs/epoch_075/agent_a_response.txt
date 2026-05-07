def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                obstacles.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    # Prefer resources we can reach no later than opponent; otherwise, reduce their lead.
    best = None
    best_key = None
    for rx, ry in resources:
        myt = cheb(sx, sy, rx, ry)
        opt = cheb(ox, oy, rx, ry)
        lead = opt - myt
        key = (lead, -myt, -abs(rx - (w - 1) / 2) - abs(ry - (h - 1) / 2))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_move_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        myt2 = cheb(nx, ny, tx, ty)
        opt2 = cheb(ox, oy, tx, ty)
        # If we are already tied/leading, focus on quickest collection; else, catch up and slightly
        # avoid giving opponent a faster path to the target.
        lead2 = opt2 - myt2
        key = (lead2, -myt2, -abs(nx - tx) - abs(ny - ty), -abs(nx - ox) - abs(ny - oy))
        if best_move_key is None or key > best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
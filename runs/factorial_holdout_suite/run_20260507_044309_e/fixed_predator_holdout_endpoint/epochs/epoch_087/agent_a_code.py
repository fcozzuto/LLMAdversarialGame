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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    tr = int(observation.get("turns_remaining") or 0)

    best = None
    best_key = None
    for rx, ry in resources:
        st = cheb(sx, sy, rx, ry)
        ot = cheb(ox, oy, rx, ry)
        if st > tr + 2:
            continue
        adv = ot - st
        key = (-(adv), st, rx + ry, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    if best is None:
        rx, ry = resources[0]
        best = (rx, ry)

    tx, ty = best

    moves = [(0, 0)]
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx or dy:
                moves.append((dx, dy))

    def valid(nx, ny):
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            return False
        if (nx, ny) in obstacles:
            return False
        return True

    best_move = (0, 0)
    best_move_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        curd = cheb(sx, sy, tx, ty)
        newd = cheb(nx, ny, tx, ty)
        # If two moves tie, prefer moving toward smaller distance and toward the target direction deterministically.
        step_key = (-(curd - newd), newd, abs(tx - nx) + abs(ty - ny), dx, dy)
        if best_move_key is None or step_key < best_move_key:
            best_move_key = step_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
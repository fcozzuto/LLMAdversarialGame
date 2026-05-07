def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                obstacles.add((px, py))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    tr = int(observation.get("turns_remaining") or 0)
    best = None
    best_key = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if (rx, ry) in obstacles:
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        if sd > tr + 2:
            continue
        adv = od - sd
        key = (-(adv), sd, rx + ry, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        rx, ry = int(resources[0][0]), int(resources[0][1])
        best = (rx, ry)

    tx, ty = best
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_move_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        nd = cheb(nx, ny, tx, ty)
        dk = (nd, abs(dx) + abs(dy), dx, dy)
        if best_move_key is None or dk < best_move_key:
            best_move_key = dk
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]
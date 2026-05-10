def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    valid = []
    for p in resources:
        x, y = p[0], p[1]
        if inb(x, y) and (x, y) not in obstacles:
            valid.append((x, y))
    if not valid:
        return [0, 0]

    best = None
    for rx, ry in valid:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd
        key = (-adv, sd, od, rx, ry)  # prefer largest advantage, then closer, then stable
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # choose move that gets us closer to target; also prefer if it worsens opponent's access (denial)
        nsd = cheb(nx, ny, tx, ty)
        nod = cheb(ox, oy, tx, ty)  # opponent position unchanged this turn
        adv_after = nod - nsd
        key = (-adv_after, nsd, abs(nx - tx) + abs(ny - ty), dx, dy)
        if best_move is None or key < best_move[0]:
            best_move = (key, [dx, dy])

    return best_move[1] if best_move is not None else [0, 0]
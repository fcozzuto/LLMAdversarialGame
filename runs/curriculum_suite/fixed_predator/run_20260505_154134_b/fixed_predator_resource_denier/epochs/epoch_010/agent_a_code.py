def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation.get('self_position', (0, 0))
    ox, oy = observation.get('opponent_position', (0, 0))
    resources = observation.get('resources', []) or []
    obstacles = set()
    for p in observation.get('obstacles', []) or []:
        try:
            obstacles.add((p[0], p[1]))
        except:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))

    if not moves:
        return [0, 0]

    best_dx, best_dy = moves[0][0], moves[0][1]

    valid_resources = [(rx, ry) for (rx, ry) in resources if (rx, ry) not in obstacles]
    if valid_resources:
        target = min(valid_resources, key=lambda r: (cheb(sx, sy, r[0], r[1]), r[0], r[1]))
        tx, ty = target
        best = None
        for dx, dy, nx, ny in moves:
            d_to_t = cheb(nx, ny, tx, ty)
            d_from_o = cheb(nx, ny, ox, oy)
            cur = (d_to_t, -d_from_o, dx, dy)
            if best is None or cur < best:
                best = cur
                best_dx, best_dy = dx, dy
        return [int(best_dx), int(best_dy)]

    best = None
    for dx, dy, nx, ny in moves:
        d_from_o = cheb(nx, ny, ox, oy)
        cur = (-d_from_o, nx, ny, dx, dy)
        if best is None or cur < best:
            best = cur
            best_dx, best_dy = dx, dy
    return [int(best_dx), int(best_dy)]
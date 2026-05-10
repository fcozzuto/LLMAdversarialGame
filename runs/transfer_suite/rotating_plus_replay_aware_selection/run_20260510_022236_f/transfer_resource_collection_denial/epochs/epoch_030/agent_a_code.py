def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)

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

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    avail = []
    for rx, ry in resources:
        rx, ry = int(rx), int(ry)
        if not inb(rx, ry) or (rx, ry) in obs:
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer resources we can arrive not later than opponent; otherwise steal as close as possible.
        key = (od - sd, -sd, -od, -(rx + 3 * ry))
        avail.append((key, (rx, ry)))
    if not avail:
        return [0, 0]
    avail.sort(key=lambda t: t[0], reverse=True)
    tx, ty = avail[0][1]

    best_move = (0, 0)
    best_key = (-10**18, -10**18, -10**18)
    # If we are on a resource, stay (deterministic).
    if (sx, sy) == (tx, ty):
        return [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        nsd = cheb(nx, ny, tx, ty)
        nod = cheb(ox, oy, tx, ty)
        # Also discourage stepping away from the "winning margin".
        cur_sd = cheb(sx, sy, tx, ty)
        cur_margin = nod - cur_sd
        new_margin = nod - nsd
        key = (new_margin, -nsd, cur_margin - new_margin)
        if key > best_key:
            best_key = key
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]
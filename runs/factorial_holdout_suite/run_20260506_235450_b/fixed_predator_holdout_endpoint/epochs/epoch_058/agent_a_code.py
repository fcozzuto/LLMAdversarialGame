def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0:
            a = -a
        b = y1 - y2
        if b < 0:
            b = -b
        return a + b

    if not resources:
        return [0, 0]

    best_val = None
    tx = ty = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        val = sd - od
        if best_val is None or val < best_val or (val == best_val and sd < best_sd) or (val == best_val and sd == best_sd and (rx < best_rx or (rx == best_rx and ry < best_ry))):
            best_val = val
            best_sd = sd
            best_rx = rx
            best_ry = ry
            tx, ty = rx, ry

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_d = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = man(nx, ny, tx, ty)
        if best_d is None or d < best_d:
            best_d = d
            best_move = [dx, dy]
    return best_move if best_d is not None else [0, 0]
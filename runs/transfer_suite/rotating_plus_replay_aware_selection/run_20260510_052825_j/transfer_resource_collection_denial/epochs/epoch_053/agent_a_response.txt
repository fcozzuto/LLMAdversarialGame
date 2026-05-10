def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles", []) or [])}

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

    valid_resources = []
    for p in resources:
        rx, ry = p[0], p[1]
        if inb(rx, ry) and (rx, ry) not in obstacles:
            valid_resources.append((rx, ry))
    if not valid_resources:
        return [0, 0]

    best_score = None
    best_t = valid_resources[0]
    for rx, ry in valid_resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd
        key = (-adv, sd, od, rx, ry)
        if best_score is None or key < best_score:
            best_score = key
            best_t = (rx, ry)

    tx, ty = best_t
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    pref = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nsd = cheb(nx, ny, tx, ty)
        nod = cheb(ox, oy, tx, ty)
        adv = nod - nsd
        pref.append((adv, nsd, (dx, dy)))
    if not pref:
        return [0, 0]

    pref.sort(key=lambda t: (-t[0], t[1], t[2][0], t[2][1]))
    return [int(pref[0][2][0]), int(pref[0][2][1])]
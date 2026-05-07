def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    resources = observation.get("resources", []) or []
    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def man(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                legal.append((dx, dy))
    legal.append((0, 0))
    if not legal:
        return [0, 0]

    best_move = None
    best_key = None

    res_list = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                res_list.append((x, y))

    if res_list:
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            min_d = 10**9
            min_d2 = 10**9
            for rx, ry in res_list:
                dd = man(nx, ny, rx, ry)
                if dd < min_d:
                    min_d2 = min_d
                    min_d = dd
                elif dd < min_d2:
                    min_d2 = dd
            opp_dist = man(nx, ny, ox, oy)
            to_corner = man(nx, ny, w - 1, h - 1)  # consistent tie-break
            key = (min_d, -opp_dist, to_corner, dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best_move = (dx, dy)
    else:
        # No visible resources: drift to opponent corner pressure
        target = (w - 1, h - 1)
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            d = man(nx, ny, target[0], target[1])
            opp_dist = man(nx, ny, ox, oy)
            key = (d, -opp_dist, dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
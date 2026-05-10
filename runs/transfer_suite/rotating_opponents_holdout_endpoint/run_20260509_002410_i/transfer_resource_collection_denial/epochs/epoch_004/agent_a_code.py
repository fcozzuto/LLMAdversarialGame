def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obstacle_set = {(p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2}

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    best = None
    bestt = None
    for rx, ry in resources:
        if (rx, ry) in obstacle_set:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach earlier; tie-break toward being closer and also affecting opponent less
        lead = do - ds
        opp_close = cheb(ox, oy, rx, ry)
        our_close = ds
        y_adv = -(abs(ry - oy) - abs(ry - sy))
        key = (lead, y_adv, -our_close, -opp_close, rx, ry)
        if best is None or key > best:
            best = key
            bestt = (rx, ry)

    if bestt is None:
        return [0, 0]
    tx, ty = bestt

    deltas = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 0), (0, 1),
              (1, -1), (1, 0), (1, 1)]

    valid = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacle_set:
            continue
        ns = cheb(nx, ny, tx, ty)
        no = cheb(ox, oy, tx, ty)
        # maximize lead after move; tie-break by staying closer and reducing opponent's advantage
        lead_after = no - ns
        key = (lead_after, -(ns), -(cheb(ox, oy, nx, ny)), -abs(ny - ty), dx, dy)
        valid.append((key, dx, dy))

    if not valid:
        return [0, 0]

    valid.sort(reverse=True)
    return [int(valid[0][1]), int(valid[0][2])]
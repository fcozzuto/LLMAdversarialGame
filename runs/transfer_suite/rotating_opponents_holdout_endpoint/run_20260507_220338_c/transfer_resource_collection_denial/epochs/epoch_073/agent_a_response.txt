def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            q = (int(p[0]), int(p[1]))
            if q not in obst:
                res.append(q)
    if not res:
        return [0, 0]

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    best = None
    best_sc = None
    for rx, ry in res:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        sc = (od - sd, -sd)
        if best is None or sc > best_sc or (sc == best_sc and (rx, ry) < best):
            best = (rx, ry)
            best_sc = sc

    tx, ty = best

    def clamp_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
            return [dx, dy]
        return None

    # Prefer diagonal/straight move toward target.
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    pref = [(dx, dy), (dx, 0), (0, dy), (0, 0), (-dx, 0), (0, -dy), (-dx, -dy)]
    options = []
    for ddx, ddy in pref:
        m = clamp_move(ddx, ddy)
        if m is not None:
            nx, ny = sx + m[0], sy + m[1]
            options.append((man(nx, ny, tx, ty), m[0], m[1]))
    if not options:
        return [0, 0]
    options.sort(key=lambda t: (t[0], t[1], t[2]))
    return [options[0][1], options[0][2]]
def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)
    resources = observation.get("resources") or []
    dxs = [-1, 0, 1]
    dys = [-1, 0, 1]
    legal = []
    for dx in dxs:
        for dy in dys:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best = None
    bestv = None

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        if resources:
            dmin = min(man(nx, ny, r[0], r[1]) for r in resources)
            tv = (-dmin, man(nx, ny, ox, oy), dx, dy)
        else:
            # If no resources known, chase center while keeping distance from opponent
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            dc = -abs(nx - cx) - abs(ny - cy)
            do = man(nx, ny, ox, oy)
            tv = (dc, do, dx, dy)
        if bestv is None or tv > bestv:
            bestv = tv
            best = (dx, dy)

    return [best[0], best[1]]
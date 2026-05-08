def choose_move(observation):
    w = int(observation.get("grid_width", 8)) or 8
    h = int(observation.get("grid_height", 8)) or 8
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    try:
        sx = int(sx)
        sy = int(sy)
        ox = int(ox)
        oy = int(oy)
    except:
        sx = sy = ox = oy = 0

    obstacles = observation.get("obstacles", []) or []
    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            try:
                oset.add((int(p[0]), int(p[1])))
            except:
                pass

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)
    options = []
    for dx in dxs:
        for dy in dys:
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny) and (nx, ny) not in oset:
                options.append((dx, dy))

    if not options:
        return [0, 0]

    target = (ox, oy)
    best = None
    best_key = None
    for dx, dy in options:
        nx, ny = sx + dx, sy + dy
        d = abs(nx - target[0]) + abs(ny - target[1])
        blocks = (nx, ny) in oset
        key = (blocks, d, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]
def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    ox, oy = int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except:
            pass

    resources = []
    for p in observation.get("resources", []) or []:
        try:
            resources.append((int(p[0]), int(p[1])))
        except:
            pass

    rem = observation.get("remaining_resource_count", None)
    use_res = False
    try:
        use_res = int(rem) > 0
    except:
        use_res = bool(resources)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x, y, a, b):
        return abs(a - x) + abs(b - y)

    target = (ox, oy)
    if use_res and resources:
        best = resources[0]
        bd = man(sx, sy, best[0], best[1])
        for r in resources[1:]:
            d = man(sx, sy, r[0], r[1])
            if d < bd:
                bd, best = d, r
        if man(sx, sy, best[0], best[1]) <= man(sx, sy, ox, oy):
            target = best

    dirs = [(0, 0), (0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1)]
    best_move = (0, 0)
    best_val = 10**18
    tx, ty = target

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        d = man(nx, ny, tx, ty)
        if (nx, ny) == (ox, oy):
            d -= 1
        if d < best_val:
            best_val = d
            best_move = [dx, dy]

    return best_move
def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles_raw = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_raw:
        if p is None or len(p) < 2:
            continue
        obstacles.add((int(p[0]), int(p[1])))

    resources_raw = observation.get("resources", []) or []
    resources = []
    for r in resources_raw:
        if r is None or len(r) < 2:
            continue
        resources.append((int(r[0]), int(r[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    def mindist_to_resources(nx, ny):
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d = abs(nx - rx) + abs(ny - ry)
            if best is None or d < best:
                best = d
        return best

    any_res = bool(resources)
    best_move = cand[0]
    best_key = None

    for dx, dy, nx, ny in cand:
        if any_res:
            dres = mindist_to_resources(nx, ny)
            if dres is None:
                dres = 10**9
            key = (dres, -abs(nx - ox) - abs(ny - oy), dx, dy)
        else:
            dome = abs(nx - ox) + abs(ny - oy)
            key = (dome, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
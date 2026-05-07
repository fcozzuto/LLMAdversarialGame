def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for o in (observation.get("obstacles", []) or []):
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in (observation.get("resources", []) or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if (x, y) not in obstacles:
                resources.append((x, y))

    if not resources and (sx, sy) not in obstacles:
        dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    def clamp_step(nx, ny):
        if nx < 0: nx = 0
        if ny < 0: ny = 0
        if nx >= w: nx = w - 1
        if ny >= h: ny = h - 1
        return nx, ny

    def best_resource_dist(nx, ny):
        best = 10**9
        for rx, ry in resources:
            d = abs(rx - nx) + abs(ry - ny)
            if d < best:
                best = d
        return best

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = 10**18
    for dx, dy in dirs:
        nx, ny = clamp_step(sx + dx, sy + dy)
        if (nx, ny) in obstacles:
            continue
        dres = best_resource_dist(nx, ny)
        dop = abs(nx - ox) + abs(ny - oy)
        score = dres
        if dop <= 2:
            score += (3 - dop) * 1000  # strongly avoid near opponent
        if (nx, ny) == (ox, oy):
            score += 1000000
        if score < best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move
def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                res.append((x, y))

    if not res:
        return [0, 0]

    def dist(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy  # Chebyshev for diagonal moves

    opp_next = dist(ox, oy, ox, oy)
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        my_best = -10**9
        for rx, ry in res:
            myd = dist(nx, ny, rx, ry)
            opd = dist(ox, oy, rx, ry)
            # Prefer resources where we can beat/deny opponent; break ties by reaching sooner.
            val = (opd - myd) * 100 + (-(myd)) * 2 + (-(opd)) * 0.1
            if val > my_best:
                my_best = val

        # Secondary: if we can't secure any advantage, move to reduce nearest resource distance.
        if my_best < -1e8:
            myd_near = min(dist(nx, ny, rx, ry) for rx, ry in res)
            val2 = -myd_near
        else:
            val2 = my_best

        key = (val2, -(abs(ox - nx) + abs(oy - ny)))
        if best_val is None or key > best_val:
            best_val = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
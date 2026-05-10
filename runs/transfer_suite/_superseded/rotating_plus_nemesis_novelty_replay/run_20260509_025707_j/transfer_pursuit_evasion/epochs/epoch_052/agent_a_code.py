def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for o in observation.get("obstacles") or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    evade = ("evader" in role) or ("runner" in role) or ("evasion" in role) or ("evasive" in role)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def bfs_dist(x0, y0, xg, yg):
        if not valid(x0, y0) or not valid(xg, yg):
            return 10**9
        if x0 == xg and y0 == yg:
            return 0
        qx = [x0]
        qy = [y0]
        qi = 0
        seen = {(x0, y0)}
        d = 0
        while qi < len(qx):
            n = len(qx)
            while qi < n:
                x = qx[qi]
                y = qy[qi]
                qi += 1
                if x == xg and y == yg:
                    return d
                for dx, dy in dirs:
                    nx, ny = x + dx, y + dy
                    if valid(nx, ny) and (nx, ny) not in seen:
                        seen.add((nx, ny))
                        qx.append(nx)
                        qy.append(ny)
            d += 1
        return 10**9

    best_move = [0, 0]
    best_key = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist = bfs_dist(nx, ny, ox, oy)
        diag = 1 if (dx != 0 and dy != 0) else 0
        stay = 1 if (dx == 0 and dy == 0) else 0
        wall_aff = min(nx, w - 1 - nx, ny, h - 1 - ny)  # smaller = closer to a wall

        if evade:
            # Increase distance; when distances tie, hug walls for wall-run tendencies.
            key = ( -dist, wall_aff, -diag, stay )
        else:
            # Reduce distance; when ties, prefer diagonal and avoid staying put.
            key = ( dist, -diag, stay )

        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move
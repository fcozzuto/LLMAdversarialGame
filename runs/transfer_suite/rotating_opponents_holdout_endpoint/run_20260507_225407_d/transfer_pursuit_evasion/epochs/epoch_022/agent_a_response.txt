def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    role = (observation.get("self_role") or "").lower()

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is None:
            continue
        obstacles.add((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inside(x, y) and (x, y) not in obstacles

    dirs8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def bfs_dist(startx, starty, goalx, goaly):
        if (startx, starty) == (goalx, goaly):
            return 0
        if not ok(startx, starty) or not ok(goalx, goaly):
            return 10**9
        qx = [startx]
        qy = [starty]
        head = 0
        dist = [[-1] * w for _ in range(h)]
        dist[starty][startx] = 0
        while head < len(qx):
            x, y = qx[head], qy[head]
            head += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs8:
                nx, ny = x + dx, y + dy
                if not ok(nx, ny):
                    continue
                if dist[ny][nx] != -1:
                    continue
                dist[ny][nx] = nd
                if nx == goalx and ny == goaly:
                    return nd
                qx.append(nx)
                qy.append(ny)
        return 10**9

    # If we are pursuer, minimize BFS distance to opponent; if evader, maximize it.
    want_min = ("pursuer" in role) or ("catcher" in role) or ("chaser" in role) or role == ""
    best = None
    best_key = None

    for dx, dy in dirs8:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = bfs_dist(nx, ny, ox, oy)
        # Secondary tie-breakers: greedy geometric progress away/toward opponent
        man = abs(nx - ox) + abs(ny - oy)
        tie = (man, nx, ny)
        key = (d, tie) if want_min else (-d, tuple([-man, -nx, -ny]))
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]
def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    if sx == ox and sy == oy:
        return [0, 0]

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def bfs_dist(startx, starty):
        if (startx, starty) == (ox, oy):
            return 0
        INF = 10**9
        dist = [[INF] * h for _ in range(w)]
        if not legal(startx, starty):
            return INF
        qx, qy = [startx], [starty]
        dist[startx][starty] = 0
        qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            d = dist[x][y] + 1
            for dx, dy in deltas:
                nx, ny = x + dx, y + dy
                if legal(nx, ny) and d < dist[nx][ny]:
                    if (nx, ny) == (ox, oy):
                        return d
                    dist[nx][ny] = d
                    qx.append(nx)
                    qy.append(ny)
        return INF

    best_move = [0, 0]
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = bfs_dist(nx, ny)
        # tie-breakers: quicker approach, then smaller resulting manhattan, then deterministic pref
        man = abs(nx - ox) + abs(ny - oy)
        key = (d, man, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]
    return best_move
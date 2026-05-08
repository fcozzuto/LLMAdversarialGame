def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    sr = str(observation.get("self_role", "")).lower()
    i_am_evader = "evader" in sr

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    INF = 10**9
    dist = [[INF] * w for _ in range(h)]
    if inb(ox, oy):
        qx, qy = [ox], [oy]
        dist[oy][ox] = 0
        qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[y][x] + 1
            for dx, dy in deltas:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx)
                    qy.append(ny)

    best_move = [0, 0]
    if i_am_evader:
        best_score = -INF
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d = dist[ny][nx]
            if d == INF:
                d = -INF
            # Prefer moving away in path-length terms; tie-break by Euclidean distance to reduce pursuit traps.
            eu = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            score = d * 1000 + eu
            if score > best_score:
                best_score = score
                best_move = [dx, dy]
    else:
        best_score = INF
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d = dist[ny][nx]
            if d == INF:
                continue
            # Prefer smallest path-length to opponent; tie-break by Manhattan alignment.
            man = abs(nx - ox) + abs(ny - oy)
            score = d * 10 + man * 0.001
            if score < best_score:
                best_score = score
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]
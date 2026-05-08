def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
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

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    anchor = max(corners, key=lambda c: manh(c, (ox, oy)))

    best_dxdy = [0, 0]
    if i_am_evader:
        best_primary = -INF
        best_secondary = -INF
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d = dist[ny][nx]
            if (nx, ny) == (ox, oy):
                continue
            if d >= INF:
                d = 10**6 + manh((nx, ny), (ox, oy))
            primary = d
            secondary = manh((nx, ny), anchor)
            if primary > best_primary or (primary == best_primary and secondary > best_secondary):
                best_primary, best_secondary = primary, secondary
                best_dxdy = [dx, dy]
    else:
        best_primary = INF
        best_secondary = -INF
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d = dist[ny][nx]
            if d >= INF:
                d = 10**6 + manh((nx, ny), (ox, oy))
            primary = d
            secondary = manh((nx, ny), (ox, oy))
            if primary < best_primary or (primary == best_primary and secondary > best_secondary):
                best_primary, best_secondary = primary, secondary
                best_dxdy = [dx, dy]

    return best_dxdy
def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    i_am_evader = "evader" in str(observation.get("self_role", "")).lower()

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

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    best = None
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = dist[ny][nx]
        if d == INF:
            d = -INF if i_am_evader else INF
        man = abs(nx - ox) + abs(ny - oy)
        to_corner = abs(nx - far_corner[0]) + abs(ny - far_corner[1])
        diag = abs(dx) + abs(dy)
        dir_bias = abs((nx - ox)) + abs((ny - oy))
        if i_am_evader:
            key = (d, man, diag, -to_corner, -dir_bias)
            if best is None or key > best_key:
                best, best_key = [dx, dy], key
        else:
            key = (-d, man, diag, to_corner, dir_bias)
            if best is None or key > best_key:
                best, best_key = [dx, dy], key
    if best is None:
        return [0, 0]
    return best
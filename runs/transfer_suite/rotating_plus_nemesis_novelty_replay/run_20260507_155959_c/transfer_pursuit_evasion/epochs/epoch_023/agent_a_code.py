def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    sr = str(observation.get("self_role", "")).lower()
    i_am_evader = "evader" in sr

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    INF = 10**9
    dist = [[INF] * w for _ in range(h)]
    if inb(ox, oy):
        q = [(ox, oy)]
        dist[oy][ox] = 0
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            nd = dist[y][x] + 1
            for dx, dy in deltas:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    q.append((nx, ny))

    best_move = (0, 0)
    best_key = -INF if i_am_evader else INF
    far_corner = max([(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)],
                     key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
        d_to_op = dist[ny][nx]
        if i_am_evader:
            if nx == ox and ny == oy:
                key = -INF
            else:
                # primary: maximize distance to pursuer; tie: drift toward far corner; tie: avoid distance=INF
                key = (d_to_op if d_to_op < INF else INF // 2)
                key = key * 1000 + (abs(far_corner[0] - nx) + abs(far_corner[1] - ny))
        else:
            # pursuer: minimize distance to evader; tie: reduce manhattan
            if nx == ox and ny == oy:
                key = -INF
            else:
                key = (d_to_op if d_to_op < INF else INF // 2)
                key = key * 1000 - (abs(nx - ox) + abs(ny - oy))
        if i_am_evader:
            if key > best_key:
                best_key = key
                best_move = (dx, dy)
        else:
            if key < best_key:
                best_key = key
                best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]
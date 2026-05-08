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

    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0

    best_move = [0, 0]
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = dist[ny][nx]
        if d == INF:
            d = -INF if i_am_evader else INF

        # tie-breaker: keep away from corners/walls for evader, toward center for pursuer
        center_score = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))
        corner = min(nx, ny, w - 1 - nx, h - 1 - ny)  # bigger => more central
        corner_pen = corner

        if i_am_evader:
            # maximize distance to pursuer; prefer more central (avoid wall-running into dead ends)
            key = (d, corner_pen, center_score, -(abs(nx - ox) + abs(ny - oy)))
            if best_key is None or key > best_key:
                best_key = key
                best_move = [dx, dy]
        else:
            # minimize distance to evader; prefer center if distances tie
            key = (-d, corner_pen, center_score, (abs(nx - ox) + abs(ny - oy)))
            if best_key is None or key > best_key:
                best_key = key
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]
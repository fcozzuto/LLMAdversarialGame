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
            d = dist[y][x] + 1
            for dx, dy in deltas:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and d < dist[ny][nx]:
                    dist[ny][nx] = d
                    qx.append(nx)
                    qy.append(ny)

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = None
    bestv = -INF if i_am_evader else INF
    best_m = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = dist[ny][nx]
        if d >= INF:
            d = 10**6 - manh((nx, ny), (ox, oy))
        m = manh((nx, ny), (ox, oy))
        if i_am_evader:
            v = d
            if v > bestv or (v == bestv and (m > (best_m if best_m is not None else -INF))):
                bestv, best_m, best = v, m, (dx, dy)
        else:
            v = d
            if v < bestv or (v == bestv and (m < (best_m if best_m is not None else INF))):
                bestv, best_m, best = v, m, (dx, dy)

    if best is None:
        # Fallback: move to increase distance if evader, decrease if pursuer
        best = (0, 0)
        bestm = -INF if i_am_evader else INF
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            m = manh((nx, ny), (ox, oy))
            if i_am_evader:
                if m > bestm:
                    bestm, best = m, (dx, dy)
            else:
                if m < bestm:
                    bestm, best = m, (dx, dy)
    return [int(best[0]), int(best[1])]
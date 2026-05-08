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

    corners = ((0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1))
    def corner_bias(x, y):
        best = 0
        for cx, cy in corners:
            d = abs(cx - x) + abs(cy - y)
            if d > best:
                best = d
        return best

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_move = (0, 0)
    best_val = -INF if i_am_evader else INF
    # deterministic tie-break: order already fixed by deltas; prefer smaller (dx,dy) lexicographically
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = dist[ny][nx]
        if d >= INF:
            d = 10**6
        # core objective: distance from opponent if evader; approach if pursuer
        if i_am_evader:
            val = d * 1000 + corner_bias(nx, ny) - manh(nx, ny, ox, oy)
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
        else:
            val = d * 1000 - corner_bias(nx, ny) + manh(nx, ny, ox, oy)
            if val < best_val:
                best_val = val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
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

    corners = ((0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1))
    def corner_score(x, y):
        best = -1
        for cx, cy in corners:
            d = (cx - x) * (cx - x) + (cy - y) * (cy - y)
            if d > best:
                best = d
        return best

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    best_val = -INF if i_am_evader else INF
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = dist[ny][nx]
        if d >= INF:
            d = manh(nx, ny, ox, oy)
        if i_am_evader:
            val = d * 1000 + corner_score(nx, ny)  # maximize distance + stay corner-heavy
            if d <= 1:
                val -= 2000  # avoid immediate capture proximity
            if val > best_val:
                best_val = val
                best = (dx, dy)
        else:
            val = d * 1000 - (corner_score(nx, ny) // 10)  # minimize distance; slightly prefer central lanes
            if d <= 1:
                val -= 100000  # strong pull into capture
            if val < best_val:
                best_val = val
                best = (dx, dy)

    if best is None:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        return [dx, dy] if not i_am_evader else [-dx, -dy]
    return [best[0], best[1]]
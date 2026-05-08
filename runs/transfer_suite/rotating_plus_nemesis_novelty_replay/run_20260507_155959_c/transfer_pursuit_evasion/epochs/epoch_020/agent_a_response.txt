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

    def corner_bias(x, y):
        best = -1
        for cx, cy in corners:
            d = abs(cx - x) + abs(cy - y)
            if d > best:
                best = d
        return best

    best = None
    if i_am_evader:
        # Maximize distance from opponent; if tie, maximize corner bias; if still tie, prefer staying still.
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx == ox and ny == oy):
                continue
            dv = dist[ny][nx]
            cb = corner_bias(nx, ny)
            cand = (dv, cb, -abs(dx) - abs(dy), -0)
            if best is None or cand > best[0]:
                best = (cand, [dx, dy])
    else:
        # Pursuer: minimize distance to opponent; if tie, prefer larger dx/dy toward opponent by BFS target.
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            dv = dist[ny][nx]
            # Also lightly bias toward direct approach to reduce zigzag chasing drift.
            direct = -(abs(nx - ox) + abs(ny - oy))
            cand = (-dv, direct, -abs(dx) - abs(dy))
            if best is None or cand > best[0]:
                best = (cand, [dx, dy])

    return best[1] if best is not None else [0, 0]
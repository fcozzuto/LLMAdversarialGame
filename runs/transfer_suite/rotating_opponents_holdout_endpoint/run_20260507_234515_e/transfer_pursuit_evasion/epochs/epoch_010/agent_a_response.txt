def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obs

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # BFS distances from opponent to all cells (8-neighborhood)
    INF = 10**9
    dist = [[INF] * h for _ in range(w)]
    if legal(ox, oy):
        dist[ox][oy] = 0
        q = [(ox, oy)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            d = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if legal(nx, ny) and d < dist[nx][ny]:
                    dist[nx][ny] = d
                    q.append((nx, ny))
    else:
        # Opponent on obstacle edge case: treat all in-bounds as reachable by Chebyshev
        for x in range(w):
            for y in range(h):
                dist[x][y] = max(abs(x - ox), abs(y - oy))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best = None
    bestv = None
    best_cheb = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = dist[nx][ny]
        c = cheb(nx, ny, ox, oy)
        # Primary: smaller BFS distance to opponent; Secondary: smaller Chebyshev distance;
        # Tertiary: prefer moving (dx,dy) that keeps directionality toward opponent.
        dir_bias = (1 if (dx == 0 and (ox - sx) == 0) else 0) + (1 if (dy == 0 and (oy - sy) == 0) else 0)
        v = (-d, -c, dir_bias, -abs(dx) - abs(dy))
        if best is None or v > bestv:
            bestv = v
            best_cheb = c
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]
def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(start):
        x0, y0 = start
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0):
            return dist
        dist[x0][y0] = 0
        q = [(x0, y0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    distO = bfs((ox, oy))

    resources_sorted = sorted((int(rx), int(ry)) for rx, ry in resources)

    best_move = (0, 0)
    best_val = -INF

    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not valid(nx, ny):
            nx, ny = sx, sy
        distS = bfs((nx, ny))
        val = 0
        # Deterministic: iterate resources in sorted order, take best advantage with tie-breaking.
        best_here = -INF
        for rx, ry in resources_sorted:
            ds = distS[rx][ry]; do = distO[rx][ry]
            if ds >= INF or do >= INF:
                continue
            # Advantage: positive if we are closer; penalty favors faster capture even when tied.
            adv = (do - ds) - (0.25 * ds)
            if adv > best_here:
                best_here = adv
        # If no reachable resources, stay still.
        if best_here <= -INF / 2:
            val = -INF
        else:
            # Small preference to reduce distance to opponent-held competition (indirectly).
            val = best_here
        if val > best_val or (val == best_val and (dxm, dym) < best_move):
            best_val = val
            best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]
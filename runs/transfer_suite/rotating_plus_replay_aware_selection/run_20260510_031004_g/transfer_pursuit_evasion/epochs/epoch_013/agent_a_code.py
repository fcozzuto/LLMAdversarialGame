def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = str(observation.get("self_role", "") or "").lower()
    opponent_role = str(observation.get("opponent_role", "") or "").lower()
    is_pursuer = ("pursuer" in self_role) or ("pursuit" in self_role) or ("hunter" in self_role)
    if not is_pursuer and (("pursuer" in opponent_role) or ("pursuit" in opponent_role) or ("hunter" in opponent_role)):
        is_pursuer = False
    if "evader" in self_role:
        is_pursuer = False

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    order = moves[:]  # fixed tie-break

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def bfs(startx, starty):
        INF = 10**9
        dist = [[INF] * h for _ in range(w)]
        if not valid(startx, starty):
            return dist
        qx, qy = [startx], [starty]
        qi = 0
        dist[startx][starty] = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx)
                    qy.append(ny)
        return dist

    # If pursuer: go to neighbor with minimum distance to opponent (shortest path distance)
    # If evader: go to neighbor with maximum distance from pursuer
    if is_pursuer:
        dist_from_op = bfs(ox, oy)
        best = None
        bestd = 10**9
        for dx, dy in order:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = dist_from_op[nx][ny]
            if d < bestd:
                bestd = d
                best = (dx, dy)
        if best is None:
            return [0, 0]
        return [best[0], best[1]]
    else:
        dist_from_self = bfs(sx, sy)  # distance from pursuer to our candidate cells
        best = None
        bestd = -1
        for dx, dy in order:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = dist_from_self[nx][ny]
            if d > bestd:
                bestd = d
                best = (dx, dy)
        if best is None:
            return [0, 0]
        return [best[0], best[1]]
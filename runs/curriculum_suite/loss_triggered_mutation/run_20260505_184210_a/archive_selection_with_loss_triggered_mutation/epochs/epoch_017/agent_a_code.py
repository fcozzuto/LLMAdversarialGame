def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles: continue
            dc = abs(nx - cx) + abs(ny - cy)
            if best is None or dc < best[0] or (dc == best[0] and (dx, dy) < best[1]):
                best = (dc, (dx, dy))
        return list(best[1]) if best else [0, 0]

    dirs = moves
    def bfs(start):
        dist = [[10**9] * h for _ in range(w)]
        if not inb(start[0], start[1]) or (start[0], start[1]) in obstacles:
            return dist
        q = [start]
        dist[start[0]][start[1]] = 0
        qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    opp_dist = bfs((ox, oy))
    best_move, best_val = (0, 0), -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        my_dist = bfs((nx, ny))
        val = -10**18
        for rx, ry in resources:
            sd = my_dist[rx][ry]
            od = opp_dist[rx][ry]
            if sd >= 10**9 or od >= 10**9:
                continue
            # Win that resource sooner; tie-break toward being closer.
            v = (od - sd) * 1000 - sd
            if v > val:
                val = v
        # If no reachable resource, fall back to moving toward nearest reachable one.
        if val == -10**18:
            mind = 10**9
            for rx, ry in resources:
                sd = my_dist[rx][ry]
                if sd < mind: mind = sd
            val = -mind
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val, best_move = val, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
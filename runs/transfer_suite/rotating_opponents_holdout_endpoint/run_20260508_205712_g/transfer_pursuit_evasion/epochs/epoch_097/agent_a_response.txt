def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    sr = str(observation.get("self_role") or "").lower()
    orr = str(observation.get("opponent_role") or "").lower()
    self_is_evader = ("evader" in sr) or ("runner" in sr)
    opp_is_evader = ("evader" in orr) or ("runner" in orr)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def bfs_dist(startx, starty):
        INF = 10**9
        dist = [[INF] * h for _ in range(w)]
        if not inb(startx, starty):
            return dist
        qx, qy = [startx], [starty]
        dist[startx][starty] = 0
        qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx)
                    qy.append(ny)
        return dist

    # If roles are unclear, assume evader when our role name contains evader; otherwise pursuer.
    target_for_dist = (ox, oy)
    dist = bfs_dist(target_for_dist[0], target_for_dist[1])

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        d = dist[nx][ny]
        val = -d if self_is_evader and not opp_is_evader else d  # evader maximizes distance; pursuer minimizes
        if best is None or val < best_val:
            best = (dx, dy)
            best_val = val
    return [int(best[0]), int(best[1])]
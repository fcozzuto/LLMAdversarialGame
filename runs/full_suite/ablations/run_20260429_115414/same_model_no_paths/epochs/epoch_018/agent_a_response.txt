def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b is not None and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        return [dx, dy]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def bfs_from(x0, y0):
        INF = 10**9
        dist = [[INF] * h for _ in range(w)]
        if (x0, y0) in obstacles:
            return dist
        dist[x0][y0] = 0
        q = [(x0, y0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    myd = bfs_from(sx, sy)
    opd = bfs_from(ox, oy)

    best = None
    for tx, ty in resources:
        d1 = myd[tx][ty]
        d2 = opd[tx][ty]
        if d1 >= 10**9 and d2 >= 10**9:
            continue
        # Prefer resources we can reach and the opponent cannot beat; also avoid being too slow.
        adv = d2 - d1
        # Deterministic tie-break: larger advantage, then smaller my distance, then closer to target center (reduces oscillation)
        key = (adv, -d1, -(abs(tx - (w - 1) // 2) + abs(ty - (h - 1) // 2)), tx, ty)
        if best is None or key > best[0]:
            best = (key, (tx, ty))
    if best is None:
        dx = 0 if sx == ox else (1 if sx < ox else -1)
        dy = 0 if sy == oy else (1 if sy < oy else -1)
        return [-dx, -dy]

    tx, ty = best[1]
    best_step = [0, 0]
    cur = myd[sx][sy]
    best_next = cur
    # Move to a neighbor with strictly smaller BFS distance to the target; else take a step that reduces it most.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            dnext = myd[nx][ny]
            if dnext < best_next:
                best_next = dnext
                best_step = [dx, dy]
    return best_step
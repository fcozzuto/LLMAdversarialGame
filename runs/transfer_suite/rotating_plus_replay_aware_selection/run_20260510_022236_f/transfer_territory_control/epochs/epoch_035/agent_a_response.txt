def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def bfs(start):
        INF = 10**9
        dist = [[INF] * h for _ in range(w)]
        if not (0 <= start[0] < w and 0 <= start[1] < h) or start in obs:
            return dist
        q = [(start[0], start[1])]
        dist[start[0]][start[1]] = 0
        head = 0
        while head < len(q):
            x, y = q[head]
            head += 1
            nd = dist[x][y] + 1
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs and nd < dist[nx][ny]:
                        dist[nx][ny] = nd
                        q.append((nx, ny))
        return dist

    my_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    if not unclaimed and not opp_terr:
        return [0, 0]

    dS = bfs((sx, sy))
    dO = bfs((ox, oy))

    candidates = []
    for x, y in unclaimed:
        if (x, y) in obs or (x, y) in my_terr:
            continue
        ds = dS[x][y]
        do = dO[x][y]
        if ds >= 10**9:
            continue
        score = (do - ds) * 3 - ds  # prefer closer to us and farther from them
        if (x, y) in opp_terr:
            score -= 5
        candidates.append((score, ds, x, y))
    # if unclaimed are empty, counterclaim opponent territory that we can reach quickly
    if not candidates:
        for x, y in opp_terr:
            if (x, y) in obs:
                continue
            ds = dS[x][y]
            do = dO[x][y]
            if ds >= 10**9:
                continue
            score = (do - ds) * 4 - ds
            candidates.append((score, ds, x, y))

    candidates.sort(reverse=True)
    tx, ty = candidates[0][2], candidates[0][3]

    dirs8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (10**9, 10**9, 0, 0)
    for dx, dy in dirs8:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        ns = dS[nx][ny]
        # secondary: closer to target
        md = abs(nx - tx) + abs(ny - ty)
        if (ns, md, dx, dy) < (best[0], best[1], best[2], best[3]):
            best = (ns, md, dx, dy)

    return [int(best[2]), int(best[3])]
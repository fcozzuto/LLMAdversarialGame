def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p[:2]) for p in (observation.get("obstacles") or []) if p and len(p) >= 2)
    unclaimed = [tuple(p[:2]) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2]
    opp_terr = [tuple(p[:2]) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2]
    cx0, cy0 = (w - 1) / 2.0, (h - 1) / 2.0

    def bfs(start):
        INF = 10**9
        dist = [[INF] * h for _ in range(w)]
        if not (0 <= start[0] < w and 0 <= start[1] < h) or start in obstacles:
            return dist
        qx, qy = [start[0]], [start[1]]
        dist[start[0]][start[1]] = 0
        qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                        if nd < dist[nx][ny]:
                            dist[nx][ny] = nd
                            qx.append(nx)
                            qy.append(ny)
        return dist

    ds = bfs((sx, sy))
    do = bfs((ox, oy))

    candidates = []
    for x, y in unclaimed:
        if (x, y) in obstacles:
            continue
        dS, dO = ds[x][y], do[x][y]
        if dS >= 10**8 or dO >= 10**8:
            continue
        cent = abs(x - cx0) + abs(y - cy0)
        candidates.append((-(dO - dS), cent, dS, x, y))
    if not candidates:
        for x, y in opp_terr:
            if (x, y) in obstacles:
                continue
            dS, dO = ds[x][y], do[x][y]
            if dS >= 10**8 or dO >= 10**8:
                continue
            cent = abs(x - cx0) + abs(y - cy0)
            candidates.append((-(dO - dS), cent, dS, x, y))
    if not candidates:
        target = (int(round(cx0)), int(round(cy0)))
    else:
        candidates.sort()
        target = (candidates[0][3], candidates[0][4])

    tx, ty = target
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if (dx, dy) == (0, 0):
                pass
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((ds[nx][ny], dx, dy, nx, ny))
    if not moves:
        return [0, 0]
    moves.sort()
    return [moves[0][1], moves[0][2]]
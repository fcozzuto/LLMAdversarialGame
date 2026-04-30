def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = {(p[0], p[1]) for p in obstacles}
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    INF = 10**9

    def bfs(start):
        x0, y0 = start
        if not (0 <= x0 < w and 0 <= y0 < h) or (x0, y0) in obs:
            return None
        dist = [[INF] * w for _ in range(h)]
        dist[y0][x0] = 0
        qx, qy = [x0], [y0]
        i = 0
        while i < len(qx):
            x, y = qx[i], qy[i]
            i += 1
            nd = dist[y][x] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx)
                    qy.append(ny)
        return dist

    if not resources:
        return [0, 0]

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))
    if myd is None or opd is None:
        return [0, 0]

    best = None
    best_key = None  # (advantage, faster)
    for rx, ry in resources:
        dm = myd[ry][rx]
        do = opd[ry][rx]
        if dm >= INF:
            continue
        adv = do - dm
        key = (adv, -dm)
        if best is None or key > best_key:
            best = (rx, ry)
            best_key = key
        elif adv == best_key[0] and -dm > best_key[1]:
            best = (rx, ry)
            best_key = key

    if best is None:
        return [0, 0]
    tx, ty = best

    cur_m = myd[sy][sx]
    cur_o = opd[sy][sx] if 0 <= sx < w and 0 <= sy < h else INF

    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        dm2 = myd[ny][nx]
        if dm2 >= INF:
            continue
        do2 = opd[ny][nx]
        adv2 = do2 - dm2
        # prioritize moving closer to target, while improving relative safety
        score = (-(dm2 + (0 if tx == nx and ty == ny else 0)), adv2, -abs(tx - nx) - abs(ty - ny))
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    # If all neighbor moves invalid, stay.
    return best_move if best_move is not None else [0, 0]
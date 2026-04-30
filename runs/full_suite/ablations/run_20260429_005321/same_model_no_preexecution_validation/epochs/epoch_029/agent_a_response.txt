def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def bfs(start):
        x0, y0 = start
        if not inb(x0, y0) or (x0, y0) in obstacles:
            return None
        dist = [[INF] * w for _ in range(h)]
        dist[y0][x0] = 0
        q = [(x0, y0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    q.append((nx, ny))
        return dist

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))
    if not resources or myd is None or opd is None:
        return [0, 0]

    best_rx, best_ry = resources[0]
    best_adv = -INF
    best_dm = INF
    for rx, ry in resources:
        dm = myd[ry][rx]; do = opd[ry][rx]
        if dm >= INF and do >= INF:
            continue
        adv = do - dm
        if adv > best_adv or (adv == best_adv and dm < best_dm):
            best_adv, best_dm = adv, dm
            best_rx, best_ry = rx, ry

    tx, ty = best_rx, best_ry
    cur = myd[sy][sx]
    best_move = (0, 0)
    best_score = (-INF, INF, 0)  # (improve, dm, opp_cheb)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dy = y1 - y2
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ndm = myd[ny][nx]
        if ndm >= INF:
            continue
        improve = cur - ndm
        opp_cheb = cheb(nx, ny, ox, oy)
        score = (improve, ndm, opp_cheb)
        if score[0] > best_score[0] or (score[0] == best_score[0] and (score[1] < best_score[1] or (score[1] == best_score[1] and score[2] < best_score[2]))):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
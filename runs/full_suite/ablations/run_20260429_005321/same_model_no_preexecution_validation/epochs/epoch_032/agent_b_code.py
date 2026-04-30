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
        if not inb(x0, y0) or (x0, y0) in obstacles: return None
        dist = [[INF] * w for _ in range(h)]
        dist[y0][x0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x = qx[qi]; y = qy[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    if not resources:
        return [0, 0]

    myd = bfs((sx, sy)); opd = bfs((ox, oy))
    if myd is None or opd is None:
        return [0, 0]

    resources_sorted = sorted(resources)
    best = None  # (score, -myd, myd, rx, ry)
    for rx, ry in resources_sorted:
        dm = myd[ry][rx]; do = opd[ry][rx]
        if dm >= INF:
            continue
        # Prefer resources we can reach sooner; boost by how much sooner than opponent.
        score = (do - dm) * 4 - dm
        cand = (score, -dm, dm, rx, ry)
        if best is None or cand > best:
            best = cand

    if best is None:
        return [0, 0]

    _, _, _, tx, ty = best
    curd = myd[sy][sx]

    best_move = [0, 0]
    best_eval = (-10**9, 0, 0)  # (improvement, -opp_improve, step_pref)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ndm = myd[ny][nx]
        if ndm >= INF:
            continue
        improvement = curd - ndm  # positive if we get closer
        # Small preference to also reduce opponent distance (when possible)
        do_now = opd[ny][nx] if opd[ny][nx] < INF else INF
        opp_improve = (opd[oy][ox] - do_now) if do_now < INF else -1000
        step_pref = 1 if (dx != 0 or dy != 0) else 0
        cand = (improvement, opp_improve, step_pref)
        if cand > best_eval:
            best_eval = cand
            best_move = [dx, dy]

    return best_move
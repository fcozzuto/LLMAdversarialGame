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

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))
    if not resources or myd is None or opd is None:
        return [0, 0]

    # Deterministic target selection: prioritize being earlier; then maximize time margin; then closeness.
    best = None
    for rx, ry in sorted(resources):
        dm = myd[ry][rx]; do = opd[ry][rx]
        if dm >= INF or do >= INF:
            continue
        margin = do - dm  # positive means we're earlier
        score = (0 if margin > 0 else 1, -margin, dm)  # later -> worse; tie -> smaller dm
        if best is None or score < best[0]:
            best = (score, rx, ry)
    if best is None:
        return [0, 0]
    _, tx, ty = best

    # Choose move that greedily reduces our distance to target; if equal, also avoid moves that give opponent immediate gain.
    curd = myd[sy][sx]
    best_move = (0, 0, INF, INF)  # (primary reduce, tie penalty, opp dist after, dx,dy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nd = myd[ny][nx]
        opp_after = opd[ny][tx] if opd is not None else INF
        reduce = curd - nd
        # primary: maximize reduce; tie: minimize nd; secondary: minimize opponent distance to target (i.e., keep it large)
        # We'll set tie penalty to nd and prefer larger opp distance.
        cand = (-(nd), -reduce, -opp_after, dx, dy)
        if best_move == (0, 0, INF, INF) or cand > (best_move[0], best_move[1], best_move[2], best_move[3], best_move[4]):
            best_move = (cand[0], cand[1], cand[2], cand[3], cand[4])

    return [int(best_move[3]), int(best_move[4])]
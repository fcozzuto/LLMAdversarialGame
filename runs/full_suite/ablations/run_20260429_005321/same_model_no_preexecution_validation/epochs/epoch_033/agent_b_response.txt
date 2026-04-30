def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def bfs(start):
        x0, y0 = start
        if not inb(x0, y0) or (x0, y0) in obs:
            return None
        dist = [[INF] * w for _ in range(h)]
        dist[y0][x0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x = qx[qi]; y = qy[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obs and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))
    if myd is None or opd is None:
        return [0, 0]

    best = None
    for rx, ry in sorted(resources):
        dm = myd[ry][rx]
        do = opd[ry][rx]
        if dm >= INF or do >= INF:
            continue
        # Prefer resources we reach sooner; break ties by maximizing opponent delay.
        score = (do - dm, -dm)
        if best is None or score > best[0]:
            best = (score, rx, ry)

    if best is None:
        return [0, 0]
    _, tx, ty = best

    # If already on target, don't move (staying may be allowed; engine accepts).
    if (sx, sy) == (tx, ty):
        return [0, 0]

    best_move = [0, 0]
    best_val = (-INF, INF, -INF)  # (adv, -my_to_target, -opp_to_target)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        dm_next = myd[ny][tx]
        do_next = opd[ny][tx]
        if dm_next >= INF:
            continue
        adv = do_next - dm_next
        val = (adv, -dm_next, -do_next)
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]
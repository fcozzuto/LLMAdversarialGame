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

    best = None
    for rx, ry in resources:
        dm, do = myd[ry][rx], opd[ry][rx]
        if dm >= INF and do >= INF:
            continue
        # Prefer resources we can reach, and where opponent is farther (higher do-dm).
        reach_bonus = 0
        if dm < INF: reach_bonus = 1
        adv = (do - dm) if (dm < INF and do < INF) else (10**6 if dm < INF else -10**6)
        cand = (reach_bonus, adv, -dm, -abs(rx - sx) - abs(ry - sy), rx, ry)
        if best is None or cand > best:
            best = cand

    if best is None:
        return [0, 0]

    _, _, _, _, tx, ty = best
    if tx == sx and ty == sy:
        return [0, 0]

    dcur = myd[sy][sx]
    best_step = [0, 0]
    best_val = (-INF, -INF)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if myd[ny][nx] >= INF:
            continue
        # Move closer along shortest paths; tie-break by improving our advantage to target.
        step_good = (myd[ny][nx] < dcur)
        if step_good:
            val1 = -(myd[ny][nx])  # prefer smaller distance to start? actually closer => smaller dist
        else:
            val1 = -INF
        val2 = -(abs(nx - tx) + abs(ny - ty))
        if (val1, val2) > best_val:
            best_val = (val1, val2)
            best_step = [dx, dy]

    return best_step
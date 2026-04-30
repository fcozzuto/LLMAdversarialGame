def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def bfs(start):
        x0, y0 = start
        dist = [[INF] * w for _ in range(h)]
        if not inb(x0, y0) or (x0, y0) in obstacles:
            return dist
        dist[y0][x0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))
    best_r = None
    best_score = -INF
    for rx, ry in resources:
        dm = myd[ry][rx]; do = opd[ry][rx]
        if dm >= INF and do >= INF:
            continue
        score = (do - dm) * 10 - dm
        if do <= dm:
            score -= 3 * (dm - do)  # discourage losing races
        if score > best_score:
            best_score = score
            best_r = (rx, ry)

    if best_r is None:
        tx, ty = w // 2, h // 2
    else:
        tx, ty = best_r

    curd = myd[ty][tx]
    best_move = (0, 0)
    best_key = (-INF, -INF)  # (target_progress, away_from_opponent)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # If target unreachable, use center; else move along distance gradient.
        if best_r is None or myd[ny][nx] >= INF or curd >= INF:
            td = abs(nx - (w // 2)) + abs(ny - (h // 2))
            target_progress = -td
        else:
            target_progress = curd - myd[ny][nx]
        away = abs(nx - ox) + abs(ny - oy)
        key = (target_progress, away)
        if key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]
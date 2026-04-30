def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    obstacles = {(int(p[0]), int(p[1])) for p in (observation.get("obstacles") or [])}
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not free(x0, y0): return dist
        dist[x0][y0] = 0
        qx, qy, qi = [x0], [y0], 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if free(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    myd = bfs(sx, sy)
    opd = bfs(ox, oy)

    best_t = None
    best_key = None
    for rx, ry in resources:
        md = myd[rx][ry]; od = opd[rx][ry]
        if md >= INF and od >= INF: 
            continue
        # Prefer resources we can reach earlier; otherwise maximize opponent delay relative to us.
        if md < INF and od < INF and md < od:
            key = (0, md, od, rx, ry)  # winning/sooner-first
        elif md < INF and od < INF:
            key = (1, -(od - md), md, rx, ry)  # denial: make (od-md) small
        elif md < INF:
            key = (0, md + 1000000, md + 1000000, rx, ry)
        else:
            key = (2, rx, ry)
        if best_key is None or key < best_key:
            best_key, best_t = key, (rx, ry)

    if best_t is None:
        # No reachable resources: move to maximize safety by moving away from opponent (minimize distance to borders irrelevant).
        tx, ty = ox, oy
    else:
        tx, ty = best_t

    # Choose neighbor that improves our distance to target; tie-break by improving relative advantage (opd - myd).
    cur_my = myd[tx][ty] if myd[tx][ty] < INF else INF
    cur_rel = (opd[tx][ty] - myd[tx][ty]) if (opd[tx][ty] < INF and myd[tx][ty] < INF) else -INF
    best_move = (0, 0)
    best_move_key = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        mdn = myd[tx][ty] if best_t is None else myd[nx][ny]  # if no target, use distance to opponent as proxy
        if best_t is None:
            # proxy: minimize Chebyshev distance to opponent (actually we want avoid, so maximize)
            dist_opp = max(abs(nx - ox), abs(ny - oy))
            rel_key = (dist_opp, -nx, -ny)
            key = (-rel_key[0], rel_key[1], rel_key[2])
        else:
            # primary: decrease our distance-to-target; secondary: maximize (opd - myd) at next cell
            my_to_t = myd[nx][tx
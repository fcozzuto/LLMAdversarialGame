def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    INF = 10**9

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def bfs(start):
        x0, y0 = start
        if not inb(x0, y0) or (x0, y0) in obstacles:
            return None
        dist = [[INF] * w for _ in range(h)]
        dist[y0][x0] = 0
        qx = [x0]
        qy = [y0]
        qi = 0
        while qi < len(qx):
            x = qx[qi]
            y = qy[qi]
            qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx)
                    qy.append(ny)
        return dist

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))
    if myd is None or opd is None:
        return [0, 0]

    best = None  # (adv, -ds, ds, rx, ry)
    for rx, ry in resources:
        ds = myd[ry][rx]
        do = opd[ry][rx]
        if ds >= INF:
            continue
        # Prefer resources where we are closer than opponent; strongly deny those where opponent is closer.
        adv = do - ds
        cand = (adv, -ds, ds, rx, ry)
        if best is None or cand > best:
            best = cand

    if best is None:
        return [0, 0]

    _, _, _, tx, ty = best

    best_move = None  # (dnext, block, dx, dy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dn = myd[ny][nx] + max(abs(tx - nx), abs(ty - ny))  # deterministic heuristic tie-break
        cand = (dn, 0, dx, dy)
        if best_move is None or cand < best_move:
            best_move = cand

    if best_move is None:
        return [0, 0]
    return [best_move[2], best_move[3]]
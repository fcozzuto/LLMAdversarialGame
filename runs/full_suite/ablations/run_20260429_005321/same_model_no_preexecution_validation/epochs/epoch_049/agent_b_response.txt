def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles_list)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (not inb(x, y)) or ((x, y) in obs)
    def bfs(start):
        x0, y0 = start
        if blocked(x0, y0): return None
        INF = 10**9
        dist = [[INF]*w for _ in range(h)]
        dist[y0][x0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if not blocked(nx, ny) and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    if not resources:
        return [0, 0]

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))
    if myd is None or opd is None:
        return [0, 0]

    INF = 10**9
    if (sx, sy) in set((r[0], r[1]) for r in resources):
        return [0, 0]

    # Choose a resource with a deterministic "winning" heuristic: maximize (opponent_time - my_time), tie-break by closer my_time
    best = None
    best_key = (-10**18, 10**18)  # (adv, mydist)
    for rx, ry in resources:
        d1 = myd[ry][rx]; d2 = opd[ry][rx]
        if d1 >= INF or d2 >= INF:
            continue
        adv = d2 - d1
        key = (adv, d1)
        if key[0] > best_key[0] or (key[0] == best_key[0] and key[1] < best_key[1]):
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]
    tx, ty = best

    # Pick a valid move that improves: primarily decrease my distance to target; secondarily increase opponent disadvantage; avoid obstacles
    curd = myd[sy][sx]
    best_move = [0, 0]
    best_val = (-10**18, -10**18)  # (improve_to_target, adv_after)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        nd1 = myd[ny][nx]
        if nd1 >= INF:
            continue
        improve = curd - nd1  # bigger is better
        nd2_here = opd[ny][nx] if opd is not None else INF
        # If both can reach, prefer making it harder for opponent relative to how close we get next
        adv_after = (nd2_here - nd1) if nd2_here < INF else -10**9
        val = (improve, adv_after)
        if val[0] > best_val[0] or (val[0] == best_val[0] and val[1] > best_val[1]):
            best_val = val
            best_move = [dx, dy]

    return best_move
def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = {(x, y) for x, y in obstacles}
    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def bfs_dist(start):
        sx0, sy0 = start
        inf = 10**9
        dist = [[inf] * h for _ in range(w)]
        if not inb(sx0, sy0) or (sx0, sy0) in obst:
            return dist
        dist[sx0][sy0] = 0
        qx, qy, qi = [sx0], [sy0], 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obst and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx)
                    qy.append(ny)
        return dist

    myd = bfs_dist((sx, sy))
    opd = bfs_dist((ox, oy))

    # Deterministic ordering for tie-breaking
    res_sorted = sorted(resources, key=lambda p: (p[0] * 8 + p[1], p[0], p[1]))

    best_move = [0, 0]
    best_val = -10**18
    my_to_opp = abs(sx - ox) + abs(sy - oy)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            val = -10**14
        else:
            # Evaluate move by (1) immediate capture chance, (2) lead over opponent at best resource,
            # (3) if opponent is ahead, deny by moving closer to their target(s).
            total = 0.0
            # Precompute distances from next position
            ndist = bfs_dist((nx, ny))
            for rx, ry in res_sorted:
                ds = ndist[rx][ry]
                do = opd[rx][ry]
                if ds >= 10**8:
                    continue
                cap = 3.0 if (nx, ny) == (rx, ry) else 0.0
                # lead: positive when we can reach no later than opponent
                lead = (do - ds)
                # Prefer capturing now; otherwise prioritize biggest lead, then closer tie-break
                val = cap + 2.2 * lead - 0.35 * ds
                # Denial term: if opponent is closer, still benefit from reducing their advantage
                if do < ds:
                    val += 0.9 * (ds - do)
                # Mild anti-zigzag: prefer moves that slightly reduce distance between agents (helps with sweep-row opponents)
                val += -0.02 * abs(nx - ox) - 0.02 * abs(ny - oy)
                total += val
            # Use opponent distance context to break ties deterministically
            val = total + 0.001 * (my_to_opp)
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]
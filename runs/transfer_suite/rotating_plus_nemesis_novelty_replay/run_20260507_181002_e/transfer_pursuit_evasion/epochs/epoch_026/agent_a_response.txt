def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    tgt_corner = max(corners, key=lambda c: abs(c[0] - sx) + abs(c[1] - sy))
    d_corner_to_opp = abs(tgt_corner[0] - ox) + abs(tgt_corner[1] - oy)
    d_best_other = min(abs(c[0] - ox) + abs(c[1] - oy) for c in corners if c != tgt_corner)

    target = [ox, oy]
    if d_corner_to_opp <= d_best_other:
        target = [tgt_corner[0], tgt_corner[1]]

    tx, ty = int(target[0]), int(target[1])

    def bfs_dist(startx, starty, goalx, goaly, limit=12):
        if not free(goalx, goaly):
            return None
        if startx == goalx and starty == goaly:
            return 0
        qx, qy = [startx], [starty]
        dist = {(startx, starty): 0}
        qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            d = dist[(x, y)]
            if d >= limit:
                continue
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if not free(nx, ny) or (nx, ny) in dist:
                    continue
                nd = d + 1
                if nx == goalx and ny == goaly:
                    return nd
                dist[(nx, ny)] = nd
                qx.append(nx)
                qy.append(ny)
        return None

    best = (10**9, 10**9, 0, 0)  # (dist, -opp_dist, dx_index, dx/dy tie-break)
    move_order = dirs
    for dx, dy in move_order:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d1 = bfs_dist(nx, ny, tx, ty, limit=14)
        if d1 is None:
            continue
        d_opp = abs(nx - ox) + abs(ny - oy)
        cand = (d1, -d_opp, dx, dy)
        if cand < best:
            best = cand
    return [int(best[2]), int(best[3])] if best[0] < 10**9 else [0, 0]
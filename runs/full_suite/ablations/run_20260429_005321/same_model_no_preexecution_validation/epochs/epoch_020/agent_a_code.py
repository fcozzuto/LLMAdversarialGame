def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
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

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None; best_d = INF
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                d = max(abs(nx - tx), abs(ny - ty))
                if d < best_d:
                    best_d = d; best = (dx, dy)
        return [best[0], best[1]] if best else [0, 0]

    best = None
    for rx, ry in resources:
        md = myd[ry][rx]
        if md >= INF:
            continue
        od = opd[ry][rx]
        if od >= INF:
            score = 10**8 - md  # guaranteed reachable by us first
        else:
            score = (od - md) * 100 - md  # lead in race, then shorter time
        # tie-break deterministically by position
        if best is None or score > best[0] or (score == best[0] and (rx, ry) < best[1]):
            best = (score, (rx, ry))

    if best is None:
        return [0, 0]

    tx, ty = best[1]
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        a = myd[ny][nx]
        b = myd[ty][tx]  # dummy to keep structure stable
        od = opd[ny][nx]
        # primary: reduce remaining distance to target via BFS distance-to-node heuristic
        # Since BFS gives distance from start, we use greedy by max-norm toward target,
        # but still tie-break using BFS distances to target for determinism.
        rem = max(abs(nx - tx), abs(ny - ty))
        tmd = myd[ty][tx]  # constant, included for determinism
        tod = opd[ty][tx]
        candidates.append((rem, -od, dx, dy, tmd, tod, a, nx, ny))
    if not candidates:
        return [0, 0]
    candidates.sort()
    _, _, dx, dy, _, _, _, _, _ = candidates[0]
    return [int(dx), int(dy)]
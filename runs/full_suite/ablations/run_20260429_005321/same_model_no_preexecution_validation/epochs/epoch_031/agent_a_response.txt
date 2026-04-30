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

    if not resources:
        return [0, 0]

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))
    if myd is None or opd is None:
        return [0, 0]

    resources_sorted = sorted(resources)
    best = None  # (advantage, -dm, rx, ry) higher advantage, then smaller dm
    for rx, ry in resources_sorted:
        dm = myd[ry][rx]; do = opd[ry][rx]
        if dm >= INF or do >= INF:
            continue
        adv = do - dm
        cand = (adv, -dm, rx, ry)
        if best is None or cand > best:
            best = cand

    if best is None:
        # fallback: go to closest resource by Euclidean-ish distance while respecting obstacles locally
        target = min(resources_sorted, key=lambda r: (abs(r[0]-sx) + abs(r[1]-sy), r[0], r[1]))
        tx, ty = target
        best_step = (INF, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                d = abs(nx - tx) + abs(ny - ty)
                cand = (-d, 0, dx, dy)
                if best_step[0] == INF or cand > best_step:
                    best_step = (-d, tx, ty, dx, dy)
        return [best_step[3], best_step[4]] if best_step[0] != INF else [0, 0]

    _, _, tx, ty = best
    curd = myd[sy][sx]

    # choose neighbor that strictly improves distance to target; else stay
    best_dxdy = (0, 0, -INF)  # dx,dy,score
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nd = myd[ny][nx]
        if nd >= curd:
            score = -((nd - curd) * 1000 + abs(nx - tx) + abs(ny - ty))
        else:
            score = 100000 - nd
        cand = (dx, dy, score)
        if cand[2] > best_dxdy[2] or (cand[2] == best_dxdy[2] and (dx, dy) < (best_dxdy[0], best_dxdy[1])):
            best_dxdy = cand

    return [int(best_dxdy[0]), int(best_dxdy[1])]
def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    INF = 10**9

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

    t = observation.get("turn_index", 0)
    best = None
    best_score = -10**18

    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        md = myd[ry][rx]
        if md >= INF:
            continue
        od = opd[ry][rx]
        if od >= INF:
            od = md + 9999
        # Prefer resources we can reach sooner than opponent; deterministic tie-break by position and turn.
        score = (od - md) * 1000 - md + ((rx * 7 + ry * 13 + t) % 5) * 0.001
        if score > best_score:
            best_score = score
            best = (rx, ry)

    if best is None:
        # No reachable resources: move toward the most open direction (avoid obstacles) toward center-ish.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best_move = (0, 0); best_val = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            val = -((nx - cx) ** 2 + (ny - cy) ** 2)
            # tiny tie-break
            val += ((nx * 3 + ny * 5 + t) % 7) * 0.001
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    tx, ty = best
    # Choose the adjacent step that decreases our distance to target; break ties by opponent distance.
    best_move = (0, 0); best_d = myd[sy][sx]; best_cmp = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = myd[ny][nx]
        if d >= INF:
            continue
        cmp = (opd[ny][nx] - d)  # larger is better
        # Prefer strictly better d; if equal, prefer higher cmp; if still equal, deterministic tie-break.
        if d < best_d or (d == best_d and (cmp > best_cmp or (cmp == best_cmp and ((nx + ny + t) % 3) > ((sx + sy + t) % 3)))):
            best_d = d; best_cmp = cmp; best_move = (dx, dy)

    return [best_move[0], best_move[1]]
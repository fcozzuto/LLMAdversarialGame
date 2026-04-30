def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    obstacles = {(int(p[0]), int(p[1])) for p in (observation.get("obstacles") or [])}
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def bfs(start):
        INF = 10**8
        dist = [[INF] * h for _ in range(w)]
        x0, y0 = int(start[0]), int(start[1])
        if not free(x0, y0): return dist
        dist[x0][y0] = 0
        q = [(x0, y0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if free(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist
    myd = bfs((sx, sy))
    opd = bfs((ox, oy))

    # Pick target: maximize (opponent advantage) = opd - myd; fall back to myd only.
    target = None
    best = -10**18
    for rx, ry in resources:
        d1, d2 = myd[rx][ry], opd[rx][ry]
        if d1 >= 10**8 and d2 >= 10**8: 
            continue
        if d1 >= 10**8: 
            score = -10**12
        elif d2 >= 10**8:
            score = 10**12
        else:
            score = (d2 - d1) * 100 - d1
        if score > best:
            best = score
            target = (rx, ry)

    # If no targets, drift toward opponent side while avoiding obstacles.
    if target is None:
        tx, ty = (w - 1 if ox < w // 2 else 0), (h - 1 if oy < h // 2 else 0)
        target = (tx, ty)

    tx, ty = target
    cur_my = myd[sx][sy]
    cur_op = opd[tx][ty]
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d_my = myd[nx][ny]
        # Prefer reaching/approaching target, and if possible, keep opponent far from it.
        # Small tie-break toward decreasing distance to opponent.
        v = 0
        if d_my < 10**8:
            v += (-d_my) * 20
            v += (opd[tx][ty] - opd[nx][ny])  # stabilizer, mostly 0
        if opd[tx][ty] < 10**8:
            v += (opd[ox][oy] - opd[ox][oy])  # deterministic no-op
        # Strongly prefer states that reduce opponent's distance to target only indirectly via relative gap:
        v += (opd[tx][ty] - myd[tx][ty] if myd[tx][ty] < 10**8 else 0) * 0.1
        # Additional: if target is reachable, prefer smaller distance-to-target directly.
        v += -myd[nx][ty] * 5
        # Tie-break: reduce distance to opponent (forces contest).
        v += -(abs(nx - ox) + abs(ny - oy))
        # If we are moving onto the target cell, huge win pressure.
        if nx == tx and ny == ty:
            v += 10**9
        if v > best_val:
            best_val = v
            best_move = (dx, dy)

    return
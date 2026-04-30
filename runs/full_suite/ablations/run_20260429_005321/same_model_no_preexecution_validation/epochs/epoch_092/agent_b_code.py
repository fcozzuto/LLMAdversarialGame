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
        INF = 10**9
        dist = [[INF] * h for _ in range(w)]
        x0, y0 = int(start[0]), int(start[1])
        if not free(x0, y0): return dist
        dist[x0][y0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if free(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))

    target = None
    best = None
    for rx, ry in resources:
        d1 = myd[rx][ry]; d2 = opd[rx][ry]
        if d1 >= 10**8: 
            continue
        # Prefer resources we can reach sooner; if tie, prefer far from opponent and close for ourselves.
        margin = (d2 - d1)
        score = (margin, -d1, -(abs(rx - ox) + abs(ry - oy)), -(rx + ry))
        if best is None or score > best:
            best = score
            target = (rx, ry)

    if target is None:
        # No reachable resources: drift toward center while avoiding obstacles.
        tx = (w - 1) // 2; ty = (h - 1) // 2
        best = None; target = (tx, ty)
    tx, ty = target

    # Greedy step toward target with deterministic tie-break.
    cx, cy = sx, sy
    best_move = (0, 0); best_key = None
    for dx, dy in dirs:
        nx, ny = cx + dx, cy + dy
        if not free(nx, ny): 
            continue
        # Primary: reduce distance to target; Secondary: win-likelihood vs opponent for that neighbor.
        d_to = max(abs(nx - tx), abs(ny - ty))  # Chebyshev
        my_after = myd[nx][ny]  # distance from start, monotonic-ish; still deterministic
        opp_after = opd[nx][ny]
        key = (-(d_to), (opp_after - my_after), -(nx + ny), dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    dx, dy = best_move
    if dx in (-1, 0, 1) and dy in (-1, 0, 1):
        return [int(dx), int(dy)]
    return [0, 0]
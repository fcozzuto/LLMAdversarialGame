def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    obstacles = {(int(p[0]), int(p[1])) for p in (observation.get("obstacles") or [])}
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles

    INF = 10**9
    def bfs(start):
        x0, y0 = int(start[0]), int(start[1])
        dist = [[INF] * h for _ in range(w)]
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

    # Choose target resource where we arrive earlier (and ideally stay ahead).
    best = None
    for rx, ry in resources:
        d1, d2 = myd[rx][ry], opd[rx][ry]
        if d1 >= INF: 
            continue
        # Prefer resources I can reach sooner; break ties by larger safety margin.
        safety = (d2 - d1)  # positive if I'm ahead
        # Slightly penalize long travel.
        val = (safety * 1000) - d1
        if best is None or val > best[0]:
            best = (val, rx, ry, d1, d2)

    # If no resources, drift toward opponent to potentially deny/contest space.
    if best is None:
        tx, ty = ox, oy
    else:
        _, tx, ty, _, _ = best
        if (sx, sy) == (tx, ty):
            return [0, 0]

    # Move one step toward target using my distance gradient; if blocked, take best alternative.
    curd = myd[tx][ty]
    best_move = (0, 0)
    best_score = -INF
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny): 
            continue
        # Prefer decreasing distance to target; tie-break by increasing opponent distance.
        nd = myd[nx][ny]
        to_t = curd - nd
        opp_far = opd[nx][ny]
        # Small deterministic bias to reduce oscillation: prefer moves with smaller (dx^2+dy^2) only when equal.
        bias = - (dx*dx + dy*dy) * 0.01
        score = to_t * 1000 + (opp_far if opp_far < INF else 0) * 0.1 + bias
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
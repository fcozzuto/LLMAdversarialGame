def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            blocked.add((p[0], p[1]))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def bfs(start):
        if not inb(start[0], start[1]):
            return None
        dist = [[-1] * h for _ in range(w)]
        q = [(start[0], start[1])]
        dist[start[0]][start[1]] = 0
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and dist[nx][ny] == -1:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    dself = bfs((sx, sy))
    dop = bfs((ox, oy))
    if dself is None or dop is None or not resources:
        return [0, 0]

    best_r = None
    best_sc = -10**9
    for rx, ry in resources:
        ds = dself[rx][ry]
        if ds == -1:
            continue
        do = dop[rx][ry]
        if do == -1:
            do = 10**6
        sc = (do - ds) - (0.15 * ds)
        if (best_r is None) or (sc > best_sc) or (sc == best_sc and ds < dself[best_r[0]][best_r[1]]):
            best_sc = sc
            best_r = (rx, ry)

    if best_r is None:
        return [0, 0]

    tx, ty = best_r
    ds = dself[tx][ty]
    if ds <= 0:
        return [0, 0]

    # Move that decreases our BFS distance the most; tie-break deterministically toward improving opponent slack.
    best_move = [0, 0]
    best_val = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dnext = dself[nx][ny]
        if dnext == -1:
            continue
        improvement = ds - dnext
        # Higher opponent advantage score is better for us; use dop to estimate contention.
        opp_slack = dop[tx][ty] - dop[nx][ny] if dop[nx][ny] != -1 else 0
        val = (10 * improvement) + opp_slack - (0.01 * (abs(nx - tx) + abs(ny - ty)))
        if (val > best_val) or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = val
            best_move = [dx, dy]

    return best_move
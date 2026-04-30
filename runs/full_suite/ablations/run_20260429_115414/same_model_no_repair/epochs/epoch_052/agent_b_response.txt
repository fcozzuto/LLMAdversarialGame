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
        qx, qy = [start[0]], [start[1]]
        head = 0
        dist[start[0]][start[1]] = 0
        while head < len(qx):
            x, y = qx[head], qy[head]
            head += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and dist[nx][ny] == -1:
                    dist[nx][ny] = nd
                    qx.append(nx)
                    qy.append(ny)
        return dist

    if not resources:
        return [0, 0]

    dself = bfs((sx, sy))
    dop = bfs((ox, oy))
    if dself is None or dop is None:
        return [0, 0]

    best = None
    for rx, ry in resources:
        ds = dself[rx][ry]
        do = dop[rx][ry]
        if ds == -1 and do == -1:
            continue
        if ds == -1:
            advantage = -10**9
        elif do == -1:
            advantage = 10**9
        else:
            advantage = do - ds  # we prefer being closer than opponent
        # Tie-break: prefer smaller ds, then deterministic by coordinates
        key = (advantage, -ds if ds != -1 else -10**9, -rx, -ry)
        if best is None or key > best[0]:
            best = (key, rx, ry, ds, do)

    if best is None:
        return [0, 0]

    _, tx, ty, _, _ = best
    # Choose next step that minimizes distance to target for us
    curd = dself[sx][sy]
    best_move = (0, 0)
    best_val = 10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ds = dself[nx][ny]
        if ds == -1:
            continue
        # Greedy: decrease distance-to-target using our BFS metric (via local move)
        # Use direct distance to target as heuristic: we don't have target distance, so compare dist to target cell in BFS:
        # BFS dist array is from current start; target cell distance is dself[tx][ty], so we want to get closer to it:
        # In this metric, smaller dist to target isn't directly available; approximate by minimizing dist from neighbor to target by BFS from start is not possible.
        # Instead: minimize neighbor's distance from our current start, and ensure eventual progress by preferring moves that reduce dself relative to neighbor-to-target:
        # We'll compute "progress" as ds_start_to_tx - ds_start_to_neighbor_to_tx approximated by (dself[tx][ty] - dself[nx][ny]) if nx can reach tx.
        # Equivalent since dself[tx][ty] is constant: maximize dself[nx][ty] closeness to dself[tx][ty] by maximizing (dself[nx][ty]) toward dself[tx][ty].
        target_dist_from_start = dself[tx][ty]
        if target_dist_from_start == -1:
            continue
        progress = target_dist_from_start - dself[nx][ny]
        # progress should be positive when dself[nx][ny] < target_dist_from_start
        val = (-progress, abs(nx - tx) + abs(ny - ty), nx, ny)
        if val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    dirs = moves

    def bfs_from(start):
        INF = 10**9
        dist = [[INF] * H for _ in range(W)]
        x0, y0 = start
        if (x0, y0) in obstacles:
            return dist
        q = [(x0, y0)]
        dist[x0][y0] = 0
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            d = dist[x][y] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles:
                    if d < dist[nx][ny]:
                        dist[nx][ny] = d
                        q.append((nx, ny))
        return dist

    dist_me = bfs_from((sx, sy))
    dist_op = bfs_from((ox, oy))

    def pick_target():
        best = None
        best_key = None
        for rx, ry in resources:
            dm = dist_me[rx][ry]
            do = dist_op[rx][ry]
            if dm >= 10**9 or do >= 10**9:
                continue
            # Primary: advantage (I arrive sooner). Secondary: maximize urgency (smaller dm).
            key = (do - dm, -dm, -(rx * 8 + ry))
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        return best

    target = pick_target()
    if target is None:
        # No reachable resources: drift deterministically toward opponent's corner.
        tx, ty = W - 1, H - 1
    else:
        tx, ty = target

    # Choose neighbor that minimizes distance to target, deterministically with tie-break.
    # Use BFS-from-target to avoid directionality issues.
    dist_t = bfs_from((tx, ty))
    best_move = (0, 0)
    best_d = dist_t[sx][sy]
    # Deterministic tie-break: prefer earlier in dirs list.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles:
            d = dist_t[nx][ny]
            if d < best_d:
                best_d = d
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
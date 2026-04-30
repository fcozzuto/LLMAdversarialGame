def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    if not resources:
        return [0, 0]
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0):
            return dist
        q = [(x0, y0)]
        dist[x0][y0] = 0
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    distS = bfs(sx, sy)
    distO = bfs(ox, oy)

    # Target selection: prefer resources we can reach earlier than opponent.
    best_target = None
    best_tscore = -10**18
    for rx, ry in resources:
        ds = distS[rx][ry]
        do = distO[rx][ry]
        if ds >= INF or do >= INF:
            continue
        # Lead first; then shorter; small preference for being already closer to target.
        tscore = (do - ds) * 100 - ds
        if (do - ds) > 0:
            tscore += 1000
        if tscore > best_tscore:
            best_tscore = tscore
            best_target = (rx, ry, ds, do)

    if best_target is None:
        return [0, 0]

    tx, ty, _, _ = best_target

    # Choose move that maximizes (lead after move) while still moving toward target.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds_next = distS[nx][ny]
        # If staying on unreachable cell (shouldn't), ignore.
        if ds_next >= INF:
            continue
        # Evaluate by looking at distance to target from this candidate.
        cur_ds_to_target = bfs(nx, ny)[tx][ty] if (tx, ty) not in obstacles else INF
        # Instead of BFS again (costly), approximate using current distS if target dist is consistent:
        # For same grid and obstacles, distS values aren't easily reusable for arbitrary nx.
        # However grid is small; BFS per candidate is acceptable (9*64*9 <= ~5000 ops).
        if cur_ds_to_target >= INF:
            continue
        do_to_target = distO[tx][ty]
        lead = do_to_target - cur_ds_to_target
        score = lead * 100 - cur_ds_to_target
        # Strongly prefer positive lead moves; discourage giving up lead.
        if lead > 0:
            score += 1000
        # Tie-break: move that reduces distance to target from current position.
        score += (distS[tx][ty] - cur_ds_to_target) * 2
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
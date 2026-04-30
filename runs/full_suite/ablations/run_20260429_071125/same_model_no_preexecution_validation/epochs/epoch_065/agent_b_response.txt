def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))

    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    INF = 10**9

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0):
            return dist
        dist[x0][y0] = 0
        q = [(x0, y0)]
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

    dself = bfs(sx, sy)
    doppo = bfs(ox, oy)

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if resources:
        best = None
        best_val = -INF
        for rx, ry in resources:
            ds = dself[rx][ry]
            do = doppo[rx][ry]
            if ds >= INF or do >= INF:
                continue
            # Prefer resources where we are closer; penalize longer time to claim.
            val = (do - ds) * 50 - ds
            # Slight tie-break: favor resources that are farther along towards opponent (more contested).
            val += (rx - sx) * 1 - (ry - sy) * 0
            if val > best_val:
                best_val = val
                best = (rx, ry)
        if best is not None:
            tx, ty = best
            best_move = None
            best_score = -INF
            for dx, dy, nx, ny in legal:
                ds_next = dself[tx][ty]
                ds_after = dself[nx][ny] + (0 if (nx, ny) == (tx, ty) else 0)
                # Use precomputed distance: distance from neighbor to target equals dist[target] from neighbor.
                # Compute via dself_target = d from neighbor to target using symmetry is not available; approximate:
                # use dself[neighbor] difference which correlates monotonically with steps on grid.
                # So score by ds_to_target = dself[tx][ty] - dself[nx][ny] (how much closer we go).
                ds_improve = ds_next - dself[nx][ny]
                opp_far = doppo[nx][ny]
                # If we can reach target quickly, heavily prioritize it.
                reach_bonus = 200 - ds_next
                score = ds_improve * 30 + opp_far - dself[nx][ny] * 2 + reach_bonus
                if score > best_score:
                    best_score = score
                    best_move = (dx, dy)
            return [int(best_move[0]), int(best_move[
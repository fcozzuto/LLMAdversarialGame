def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    inf = 10**9

    def bfs(start):
        q = [start]
        dist = [[inf] * h for _ in range(w)]
        if start in obstacles:
            return dist
        dist[start[0]][start[1]] = 0
        head = 0
        while head < len(q):
            x, y = q[head]
            head += 1
            nd = dist[x][y] + 1
            for dx, dy in deltas:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    ds = bfs((sx, sy))
    do = bfs((ox, oy))

    def res_key(r):
        x, y = r
        sd = ds[x][y]
        od = do[x][y]
        if sd >= inf and od >= inf:
            score = -inf
        else:
            if sd >= inf:
                sd = inf
            if od >= inf:
                od = inf
            # Prefer resources we can reach and likely secure.
            score = (od - sd) * 10 - sd
            # Mild center preference for tie-break stability.
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            score -= (abs(x - cx) + abs(y - cy)) * 0.01
        return (-score, x, y)

    resources_sorted = sorted(resources, key=res_key)
    tx, ty = resources_sorted[0]

    best_move = (0, 0)
    best_d = inf
    best_score = -inf
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        d = ds[nx][ny]
        if d < best_d:
            best_d = d
            best_move = (dx, dy)
            best_score = (do[tx][ty] - ds[nx][ny])
        elif d == best_d:
            score = (do[tx][ty] - ds[nx][ny])
            if score > best_score or (score == best_score and (dx, dy) < best_move):
                best_move = (dx, dy)
                best_score = score

    return [int(best_move[0]), int(best_move[1])]
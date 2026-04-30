def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    if not resources:
        return [0, 0]

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

    distS = bfs(sx, sy)
    distO = bfs(ox, oy)

    # Choose target: prefer reachable with advantage; otherwise closest reachable.
    best = None
    best_key = None
    for rx, ry in resources:
        ds = distS[rx][ry]
        if ds >= INF:
            continue
        do = distO[rx][ry]
        # Key: maximize (do - ds), then minimize ds
        key = (-(do - ds), ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        # If none reachable (rare), just move to reduce distance to any non-obstacle cell toward opponent/resources.
        tx, ty = resources[0]
        bestd = INF
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                d = max(abs(nx - tx), abs(ny - ty))
                if d < bestd:
                    bestd = d
                    best_move = [dx, dy]
        return best_move if "best_move" in locals() else [0, 0]

    tx, ty = best
    curd = distS[tx][ty]
    # Move greedily: step that most reduces distS to target; tie-break by increasing distO (deny opponent).
    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nds = distS[nx][ny]
        if nds >= INF:
            continue
        ndn = distO[nx][ny]
        # Primary: smaller distance to target; Secondary: farther from opponent's distance to target (deny); Tertiary deterministic.
        score = (nds, -(ndn), dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    # If somehow no improving move found, allow staying.
    return best_move
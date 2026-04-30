def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]) or [0, 0])
    ox, oy = map(int, observation.get("opponent_position", [0, 0]) or [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    dirs = [(-1, -1),(0, -1),(1, -1),(-1, 0),(0, 0),(1, 0),(-1, 1),(0, 1),(1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def bfs_from(px, py):
        INF = 10**9
        dist = [[INF] * h for _ in range(w)]
        if not inb(px, py) or (px, py) in obs:
            return dist
        qx = [px]
        qy = [py]
        head = 0
        dist[px][py] = 0
        while head < len(qx):
            x, y = qx[head], qy[head]
            head += 1
            nd = dist[x][y] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obs and dist[nx][ny] > nd:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    vis_res = []
    for r in resources:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                vis_res.append((x, y))

    dist_s = bfs_from(sx, sy)
    dist_o = bfs_from(ox, oy)

    remaining = int(observation.get("remaining_resource_count", 0) or 0)

    if vis_res:
        # Prefer resources where we can arrive no later than opponent (or closest advantage),
        # and in tie, closer to us; otherwise, farther from opponent to reduce their contest.
        best = None
        best_key = None
        for rx, ry in vis_res:
            ds = dist_s[rx][ry]
            do = dist_o[rx][ry]
            if ds >= 10**8:  # unreachable
                continue
            margin = ds - do
            # When few resources remain, prioritize contest/steal more aggressively.
            steal_weight = 3 if remaining <= 4 else 1
            key = (margin * steal_weight, ds, -cheb(rx, ry, ox, oy))
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best if best is not None else (sx, sy)
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    # Choose one step that decreases our distance to target; break ties by contest safety.
    best_move = (0, 0)
    best_val = None
    cur_ds = dist_s[tx][ty] if 0 <= tx < w and 0 <= ty < h else 0
    for
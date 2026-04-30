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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    def bfs(start):
        if not inb(start[0], start[1]):
            return None
        dist = [[-1] * h for _ in range(w)]
        q = [(start[0], start[1])]
        dist[start[0]][start[1]] = 0
        head = 0
        while head < len(q):
            x, y = q[head]
            head += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and dist[nx][ny] == -1:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    dself = bfs((sx, sy))
    dop = bfs((ox, oy))
    if dself is None or dop is None:
        return [0, 0]

    def cheb_dist(x, y, tx, ty):
        dx = x - tx
        if dx < 0: dx = -dx
        dy = y - ty
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    # Choose target resource maximizing advantage: (opponent far) - (we close), tie-break by closer Chebyshev
    best_t = None
    best_key = None
    for tx, ty in resources:
        ds = dself[tx][ty] if 0 <= tx < w and 0 <= ty < h else -1
        do = dop[tx][ty] if 0 <= tx < w and 0 <= ty < h else -1
        if ds == -1:
            continue
        if do == -1:
            do = 10**9
        adv = (do - ds)  # bigger is better
        # Tie-break: prefer immediate proximity to reduce path stagnation
        proximity = -cheb_dist(sx, sy, tx, ty)
        key = (adv, proximity, -tx, -ty)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (tx, ty)

    if best_t is None:
        return [0, 0]
    tx, ty = best_t

    # Move choice: among legal moves, minimize (our distance to target) and maximize chance of arriving first
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            legal.append((nx, ny, dx, dy))
    if not legal:
        return [0, 0]

    best = None
    best_val = None
    for nx, ny, dx, dy in legal:
        ds_step = dself[tx][ty] if dself[tx][ty] != -1 else 10**9
        do_to_target = dop[tx][ty] if dop[tx][ty] != -1 else 10**9
        # If we could be at target in one less step by moving toward it, reflect via Chebyshev improvement
        before = cheb_dist(sx, sy, tx, ty)
        after = cheb_dist(nx, ny, tx, ty)
        arrive_gain = before - after  # positive is good
        val = (-(ds_step), arrive_gain, (do_to_target - (ds_step if ds_step < 10**9 else 10**9)), -tx, -ty)
        if best_val is None or val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]
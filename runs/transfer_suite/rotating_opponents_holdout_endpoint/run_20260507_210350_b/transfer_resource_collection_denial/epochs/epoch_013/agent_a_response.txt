def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    resources = [tuple(p) for p in observation["resources"] if tuple(p) not in obstacles]
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def bfs(start):
        sx0, sy0 = start
        dist = {(sx0, sy0): 0}
        q = [(sx0, sy0)]
        head = 0
        while head < len(q):
            x, y = q[head]
            head += 1
            d = dist[(x, y)]
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in dist:
                    dist[(nx, ny)] = d + 1
                    q.append((nx, ny))
        return dist

    ds = bfs((sx, sy))
    do = bfs((ox, oy))

    # Target with priority: we arrive earlier (bigger margin), then fewer steps overall, then far from opponent (tie-break).
    best = None
    best_key = None
    for tx, ty in resources:
        if (tx, ty) not in ds:
            continue
        d1 = ds[(tx, ty)]
        d2 = do.get((tx, ty), 10**9)
        margin = d2 - d1
        key = (-margin, d1, abs(tx - ox) + abs(ty - oy) * 1e-3, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best = (tx, ty)

    if best is None:
        # Fallback: go to closest reachable resource.
        best = min(resources, key=lambda p: ds.get(p, 10**9))

    tx, ty = best
    cur_d = ds.get((sx, sy), 10**9)

    best_move = [0, 0]
    best_md = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nd = ds.get((nx, ny), 10**9)
        # Prefer decreasing our distance; if stuck, maximize opponent delay.
        md_opp = do.get((tx, ty), 10**9) - (do.get((nx, ny), 10**9))
        key = (nd - cur_d, -md_opp, abs(nx - ox) + abs(ny - oy) * 1e-3, dx, dy)
        if best_md is None or key < best_md:
            best_md = key
            best_move = [dx, dy]
    return best_move
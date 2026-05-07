def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def bfs(start):
        dist = {}
        if start in obstacles:
            return dist
        q = [start]
        dist[start] = 0
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            d = dist[(x, y)] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and (nx, ny) not in dist:
                    dist[(nx, ny)] = d
                    q.append((nx, ny))
        return dist

    ds = bfs((sx, sy))
    do = bfs((ox, oy))

    best = None
    best_key = None
    for r in resources:
        rx, ry = r
        if (rx, ry) in obstacles:
            continue
        if (rx, ry) not in ds:
            continue
        sd = ds[(rx, ry)]
        od = do.get((rx, ry), 10**9)
        key = (od - sd, -sd, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        tx, ty = ox, oy
    else:
        tx, ty = best

    if (sx, sy) == (tx, ty):
        return [0, 0]

    target_dist = ds.get((tx, ty), 10**9)
    best_step = [0, 0]
    best_step_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nd = ds.get((nx, ny), 10**9)
        # Prefer steps that reduce our remaining distance to target; tie-break by increasing opponent's distance to target.
        step_key = (-abs(target_dist - nd), -nd, do.get((nx, ny), 10**9))
        if best_step_key is None or step_key > best_step_key:
            best_step_key = step_key
            best_step = [dx, dy]

    return best_step
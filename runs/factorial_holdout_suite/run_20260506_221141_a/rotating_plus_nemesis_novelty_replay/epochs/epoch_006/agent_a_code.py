def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set((x, y) for x, y in obstacles)

    if not resources:
        return [0, 0]

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh and (x, y) not in obs

    def bfs_dist(start, goal, limit=18):
        if start == goal:
            return 0
        q = [start]
        head = 0
        dist = {start: 0}
        while head < len(q):
            x, y = q[head]
            head += 1
            d = dist[(x, y)]
            if d >= limit:
                continue
            for dx, dy in moves[1:]:
                nx, ny = x + dx, y + dy
                if not inb(nx, ny):
                    continue
                nd = d + 1
                if (nx, ny) == goal:
                    return nd
                if (nx, ny) not in dist:
                    dist[(nx, ny)] = nd
                    q.append((nx, ny))
        return None

    best_r = None
    best_key = None
    for rx, ry in resources:
        sd = bfs_dist((sx, sy), (rx, ry))
        od = bfs_dist((ox, oy), (rx, ry))
        if sd is None and od is None:
            continue
        if sd is None:
            key = (-10**6, 10**6)  # can't reach, avoid
        elif od is None:
            key = (10**6, -10**6)  # we can reach, opponent can't
        else:
            advantage = od - sd
            # tie-break: prefer smaller own distance
            key = (advantage, -sd)
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r
    cur_sd = bfs_dist((sx, sy), (tx, ty))
    if cur_sd is None:
        # fall back: greedy towards nearest reachable resource in straight line, avoid obstacles only
        target = min(resources, key=lambda r: (abs(sx - r[0]) + abs(sy - r[1])))
        tx, ty = target

    best_move = [0, 0]
    best_move_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nsd = bfs_dist((nx, ny), (tx, ty))
        if nsd is None:
            continue
        nosd = bfs_dist((ox, oy), (tx, ty))
        # Interceptor-like tweak: prefer moves that reduce our distance more than they reduce opponent's
        key = (-nsd, (nosd if nosd is not None else 99) - nsd, abs(nx - tx) + abs(ny - ty))
        if best_move_key is None or key > best_move_key:
            best_move_key = key
            best_move = [dx, dy]

    return best_move
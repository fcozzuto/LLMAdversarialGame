def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)
    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0),  (0, 0),  (1, 0),
              (-1, 1),  (0, 1),  (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs_from(start):
        sx0, sy0 = start
        if not ok(sx0, sy0):
            return {}
        dist = {(sx0, sy0): 0}
        q = [(sx0, sy0)]
        i = 0
        while i < len(q):
            x, y = q[i]; i += 1
            d = dist[(x, y)] + 1
            for dx, dy in deltas:
                nx, ny = x + dx, y + dy
                if ok(nx, ny) and (nx, ny) not in dist:
                    dist[(nx, ny)] = d
                    q.append((nx, ny))
        return dist

    ds = bfs_from((sx, sy))
    do = bfs_from((ox, oy))

    best_target = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) not in ds and (rx, ry) not in do:
            continue
        self_d = ds.get((rx, ry), 10**9)
        opp_d = do.get((rx, ry), 10**9)
        # Prefer we arrive sooner; then faster self; then deterministic coordinate tie-break
        key = (self_d - opp_d, self_d, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    if best_target is None:
        # Fallback: greedily move toward any in-bounds non-obstacle resource
        tx, ty = resources[0]
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        if ok(sx + dx, sy + dy):
            return [dx, dy]
        if ok(sx + dx, sy): return [dx, 0]
        if ok(sx, sy + dy): return [0, dy]
        return [0, 0]

    tx, ty = best_target
    best_move = [0, 0]
    best_move_key = None

    # Evaluate neighbor positions with BFS distance to target
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if (nx, ny) == (sx, sy) and (dx, dy) != (0, 0):
            continue
        dn = bfs_from((nx, ny)).get((tx, ty), 10**9)
        # Opponent remains; bias toward reducing our distance to the target and increasing (self_d - opp_d)
        opp_d = do.get((tx, ty), 10**9)
        self_adv = dn - opp_d
        # If target is unreachable, deprioritize heavily
        key = (self_adv, dn, abs(nx - tx) + abs(ny - ty), nx, ny)
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = [dx, dy]

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]
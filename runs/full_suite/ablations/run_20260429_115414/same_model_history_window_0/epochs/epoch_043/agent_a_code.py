def choose_move(observation):
    W = observation.get('grid_width', 8)
    H = observation.get('grid_height', 8)
    sx, sy = observation['self_position']
    ox, oy = observation['opponent_position']
    obstacles = observation.get('obstacles', [])
    resources = observation.get('resources', [])
    obst = set((x, y) for x, y in obstacles)
    if not resources:
        # No resources: drift to reduce distance to opponent while staying safe
        best = (10**9, [0, 0])
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if not (0 <= nx < W and 0 <= ny < H): 
                    continue
                if (nx, ny) in obst: 
                    continue
                d = abs(nx - ox) + abs(ny - oy)
                if d < best[0]:
                    best = (d, [dx, dy])
        return best[1]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best_key = None
    best_target = resources[0]
    for r in resources:
        rt = (r[0], r[1])
        ds = dist((sx, sy), rt)
        do = dist((ox, oy), rt)
        # Prefer resources closer to us than opponent; tie-break deterministically by coords
        key = (do - ds, -ds, rt[0], rt[1])
        if best_key is None or key > best_key:
            best_key = key
            best_target = rt

    tx, ty = best_target
    # Greedy step toward target; if blocked, try best among legal moves
    move_order = []
    primary_dx = 0 if tx == sx else (1 if tx > sx else -1)
    primary_dy = 0 if ty == sy else (1 if ty > sy else -1)
    move_order.append([primary_dx, primary_dy])
    # Remaining 8 moves in deterministic order
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            m = [dx, dy]
            if m == [primary_dx, primary_dy]:
                continue
            move_order.append(m)

    def legal(nx, ny):
        return 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obst

    best_move = None
    best_score = None
    for dx, dy in move_order:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # Score: minimize distance to target; break ties by maximizing advantage vs opponent; then coords
        d_t = dist((nx, ny), (tx, ty))
        adv = dist((ox, oy), (tx, ty)) - d_t
        score = (d_t, -adv, nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]
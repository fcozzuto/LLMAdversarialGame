def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst

    if not res:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Evaluate move by best target: prefer moves that make us strictly closer than opponent.
    best_move, best_val = (0, 0), -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my = (nx, ny)
        val = -dist(my, (ox, oy)) * 0.01  # slight pressure away from opponent
        for t in res:
            d_me = dist(my, t)
            d_op = dist((ox, oy), t)
            # Primary: maximize advantage; Secondary: minimize our distance
            adv = d_op - d_me  # positive if we are closer
            # Big weight on advantage to secure pickups; tie-break by closeness and deterministic ordering.
            v = (adv * 1000) - (d_me * 2) + ((d_me == 0) * 5000)
            if v > val:
                val = v
        # Deterministic tie-break: prefer smaller lexicographic move
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val, best_move = val, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
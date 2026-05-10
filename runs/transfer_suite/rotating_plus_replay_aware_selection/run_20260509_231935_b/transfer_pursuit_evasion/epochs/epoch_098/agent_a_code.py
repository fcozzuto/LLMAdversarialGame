def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs_set = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    sr = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("pursuer" in sr) or ("pursue" in sr)

    moves = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    pref = [(0,0), (1,1), (-1,-1), (1,-1), (-1,1), (1,0), (-1,0), (0,1), (0,-1)]
    order = [m for m in pref if m in moves] + [m for m in moves if m not in pref]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_set

    def manhattan(x, y):
        return abs(x - ox) + abs(y - oy)

    def free_neighbors(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if ok(nx, ny):
                c += 1
        return c

    best_move = (0, 0)
    best_val = None
    best_free = None

    for dx, dy in order:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = manhattan(nx, ny)
        fn = free_neighbors(nx, ny)
        val = -d if is_pursuer else d
        if best_val is None or val > best_val or (val == best_val and ((fn > best_free) if is_pursuer else (fn < best_free))):
            best_val = val
            best_free = fn
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
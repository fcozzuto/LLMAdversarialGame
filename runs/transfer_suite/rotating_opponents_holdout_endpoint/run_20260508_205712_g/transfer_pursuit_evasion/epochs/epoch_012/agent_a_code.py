def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for a in observation.get("obstacles", []) or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            obs.add((int(a[0]), int(a[1])))

    capture_radius = int(observation.get("capture_radius", 0))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (x, y) in obs
    def md(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    my_role = str(observation.get("self_role", "")).lower()
    is_pursuer = ("purs" in my_role) or ("chase" in my_role) or ("catch" in my_role)

    def mobility(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and not blocked(nx, ny):
                c += 1
        return c

    best = None
    best_move = (0, 0)
    # deterministic tie-break by nx,ny after primary keys
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        d = md(nx, ny, ox, oy)
        opp_m = mobility(ox, oy)
        my_m = mobility(nx, ny)

        if is_pursuer:
            # Prefer immediate capture, then minimize distance, then constrain opponent (low opponent mobility),
            # then choose low-distance squares with low mobility.
            primary = -1 if d <= capture_radius else 0
            key = (
                primary,                   # capture first
                -d,                        # smaller d is better -> use negative to maximize
                -(opp_m),                  # smaller opponent mobility better
                -my_m,                     # smaller my mobility better (less self branching under pursuit)
                nx, ny
            )
            better = (best is None) or (key > best)
        else:
            # Evader: maximize distance, prefer moves that keep higher mobility and avoid letting pursuer have easy escape.
            primary = 1 if d > capture_radius else 0
            key = (
                primary,                   # being uncaptured preferred
                d,                         # larger d better
                my_m,                      # higher self mobility
                -opp_m,                    # lower opponent mobility better
                nx, ny
            )
            better = (best is None) or (key > best)

        if better:
            best = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
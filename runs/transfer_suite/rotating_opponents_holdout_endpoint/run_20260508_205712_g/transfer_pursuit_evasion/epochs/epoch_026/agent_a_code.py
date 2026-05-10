def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    obstacles = set()
    for a in observation.get("obstacles", []) or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            obstacles.add((int(a[0]), int(a[1])))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    role = observation.get("self_role", "pursuer")
    best_move = [0, 0]
    best_val = None
    # deterministic tie-break: fixed order + strict comparison

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        dist = cheb(nx, ny, ox, oy)

        # obstacle pressure + local mobility (avoid trapping against walls/obstacles)
        occ_adj = 0
        mob = 0
        for adx, ady in moves:
            ax, ay = nx + adx, ny + ady
            if 0 <= ax < w and 0 <= ay < h:
                if (ax, ay) in obstacles:
                    occ_adj += 1
                if (ax, ay) not in obstacles:
                    mob += 1

        # keep away from edges slightly (evader) or keep centered slightly (pursuer)
        edge = min(nx, ny, w - 1 - nx, h - 1 - ny)

        # score design
        if role == "evader":
            # primary: maximize distance
            val = dist
            # secondary: maximize mobility, keep away from walls/obstacles, avoid being boxed near obstacles
            val = (val * 1000) + (mob * 10) + (edge * 2) - (occ_adj * 5)
        else:
            # pursuer: minimize distance; also prefer moves with better mobility so you keep pressure
            val = -dist
            val = (val * 1000) + (mob * 6) + (edge * 1) - (occ_adj * 5)

        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]
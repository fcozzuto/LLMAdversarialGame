def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    if not resources:
        return [0, 0]

    opp_corner_bias = (ox + oy) - ((w - 1 - sx) + (h - 1 - sy))
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        my_best = -10**9
        for rx, ry in resources:
            dm = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Positive favors us arriving earlier; stronger when winning by margin.
            advantage = (do - dm)
            # If opponent is closer, prefer moves that reduce their advantage (contestation).
            contest = -advantage if advantage > 0 else (-advantage * 0.5)
            # Slightly prefer resources nearer to our direction of travel and away from center stalls.
            center = (rx - (w - 1) / 2.0) ** 2 + (ry - (h - 1) / 2.0) ** 2
            # Small tie-breaker: move that also reduces distance to opponent to enable denial.
            deny = -cheb(nx, ny, ox, oy) * 0.01
            score = (advantage * 50.0) + contest + deny - center * 0.001
            if score > my_best:
                my_best = score
        # Bias deterministically toward breaking symmetry: go toward the "dominant" direction if tied.
        sym = -cheb(nx, ny, (w - 1 - ox), (h - 1 - oy)) * 0.0001 - opp_corner_bias * 0.00001
        total = my_best + sym
        key = (round(total, 6), -(dx * 3 + dy))
        if best is None or key > best[0]:
            best = (key, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]
def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        d1 = ax - bx
        if d1 < 0:
            d1 = -d1
        d2 = ay - by
        if d2 < 0:
            d2 = -d2
        return d1 + d2

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_move = [0, 0]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not cell_ok(nx, ny):
            nx, ny = sx, sy

        my_best_adv = -10**9
        my_best_my_d = 10**9

        for rx, ry in resources:
            if not cell_ok(rx, ry):
                continue
            my_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            adv = opp_d - my_d  # positive means we are closer
            if adv > my_best_adv or (adv == my_best_adv and my_d < my_best_my_d):
                my_best_adv = adv
                my_best_my_d = my_d

        # Primary: maximize advantage; Secondary: minimize my distance to that best resource
        # Tertiary: tie-break toward staying close to current direction (prefer diagonal slightly)
        dir_pref = (dx != 0 and dy != 0)
        key = (my_best_adv, -my_best_my_d, int(dir_pref))
        if best is None or key > best:
            best = key
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]
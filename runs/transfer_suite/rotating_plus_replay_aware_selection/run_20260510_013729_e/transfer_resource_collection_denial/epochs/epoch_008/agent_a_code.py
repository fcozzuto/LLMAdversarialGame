def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation["grid_width"]
    h = observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obstacle_set = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacle_set

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0:
            dx = -dx
        dy = y2 - y1
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    if not resources:
        return [0, 0]

    best_move = (0, 0)
    best_val = None

    # Determine if we can "win" any resource (currently not worse than opponent).
    any_winnable = False
    for rx, ry in resources:
        if cheb(sx, sy, rx, ry) <= cheb(ox, oy, rx, ry):
            any_winnable = True
            break

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        my_best = -10**9
        for rx, ry in resources:
            dm = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - dm  # positive favors us

            # If none are currently winnable, aim to "deny": go toward a resource
            # that is currently closest to the opponent (reduce their chance).
            if any_winnable:
                val = adv * 1000 - dm
            else:
                val = -do * 1000 - dm + adv * 50

            # Prefer slightly earlier capture (smaller dm).
            val += (1.0 / (1 + dm)) * 5

            if val > my_best:
                my_best = val

        if best_val is None or my_best > best_val:
            best_val = my_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
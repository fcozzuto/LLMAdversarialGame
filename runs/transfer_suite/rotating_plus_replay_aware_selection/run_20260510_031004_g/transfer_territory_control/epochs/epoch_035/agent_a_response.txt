def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    px, py = observation.get("opponent_position", (0, 0))

    obstacles = set(map(tuple, observation.get("obstacles", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    self_terr = set(map(tuple, observation.get("self_territory", [])))
    opp_terr = set(map(tuple, observation.get("opponent_territory", [])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        dist_op = max(abs(nx - px), abs(ny - py))
        val = 0

        if (nx, ny) in opp_terr:
            val = 900 - 3 * dist_op
        elif (nx, ny) in unclaimed:
            val = 280 - 6 * dist_op
        elif (nx, ny) in self_terr:
            val = 140 - dist_op
        else:
            val = -2 * dist_op

        # Frontline shaping: prefer cells adjacent to opponent territory/unclaimed
        adj_opp = 0
        adj_un = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if not inb(tx, ty) or (tx, ty) in obstacles:
                    continue
                if (tx, ty) in opp_terr:
                    adj_opp += 1
                if (tx, ty) in unclaimed:
                    adj_un += 1
        val += 20 * adj_un + 25 * adj_opp

        # Nudge away if too close and not gaining anything
        if val < 200 and dist_op <= 1:
            val -= 80

        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]
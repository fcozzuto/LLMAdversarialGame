def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    px, py = observation.get("opponent_position", (0, 0))

    obstacles = set(map(tuple, observation.get("obstacles", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    self_terr = set(map(tuple, observation.get("self_territory", [])))
    opp_terr = set(map(tuple, observation.get("opponent_territory", [])))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def neigh_counts(x, y):
        cu = 0
        ct = 0
        co = 0
        for dx, dy in dirs:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            if (nx, ny) in unclaimed:
                cu += 1
            elif (nx, ny) in self_terr:
                ct += 1
            elif (nx, ny) in opp_terr:
                co += 1
        return cu, ct, co

    best = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        val = 0
        if (nx, ny) in unclaimed:
            val += 450
        if (nx, ny) in self_terr:
            val += 18
        if (nx, ny) in opp_terr:
            cu, ct, co = neigh_counts(nx, ny)
            val += 220 + 35 * cu - 25 * co + 10 * ct
            # discourage being isolated inside opponent territory
            val -= 20 * (max(abs(nx - px), abs(ny - py)) <= 1)
        if (nx, ny) not in unclaimed and (nx, ny) not in self_terr and (nx, ny) not in opp_terr:
            val -= 40

        # frontier pressure: move toward opponent when it opens unclaimed, else toward unclaimed
        disto = abs(nx - px) + abs(ny - py)
        val += 10 * (-disto // 2)

        cu, ct, co = neigh_counts(nx, ny)
        val += 25 * cu + 6 * ct - 10 * co

        if val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]
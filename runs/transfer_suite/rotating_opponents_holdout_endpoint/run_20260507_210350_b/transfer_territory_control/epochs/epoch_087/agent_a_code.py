def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)

    obstacles = set(map(tuple, observation.get("obstacles") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def cell_base(x, y):
        if (x, y) in obstacles:
            return -10**9
        if (x, y) in self_terr:
            return 2.0
        if (x, y) in unclaimed:
            return 10.0
        if (x, y) in opp_terr:
            return 6.5
        return 3.5

    def frontier_value(x, y):
        c = 0
        for ax, ay in dirs:
            nx, ny = x + ax, y + ay
            if inb(nx, ny) and (nx, ny) in unclaimed:
                c += 1
        return c

    def opp_pressure(x, y):
        # how many neighbor cells are opponent-owned (risk of being countered)
        c = 0
        for ax, ay in dirs:
            nx, ny = x + ax, y + ay
            if inb(nx, ny) and (nx, ny) in opp_terr:
                c += 1
        return c

    # Prefer conquering unclaimed/frontier; secondarily move toward center; penalize high opponent-pressure
    best_score = float("-inf")
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        val = 0
        val += cell_base(nx, ny)
        val += 1.2 * frontier_value(nx, ny)
        val += -0.6 * opp_pressure(nx, ny)
        val += -0.02 * (abs(nx - cx) + abs(ny - cy))
        # Deterministic tie-break: non-stay, then dx, then dy
        move_rank = (1 if (dx == 0 and dy == 0) else 0, dx, dy)
        if val > best_score or (val == best_score and move_rank < (1 if best_move == (0, 0) else 0, best_move[0], best_move[1])):
            best_score = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
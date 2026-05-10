def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory", []) or []))
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells", []) or []))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    turn = int(observation.get("turn_index", 0))

    dirs8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj4_count(x, y, S):
        c = 0
        for dx, dy in dirs4:
            if (x + dx, y + dy) in S:
                c += 1
        return c

    def min_manhattan_to_opp(x, y):
        return abs(ox - x) + abs(oy - y)

    def min_dist_to_obstacle(x, y):
        # small local check: within Chebyshev radius 3
        best = 10**9
        for ex, ey in obstacles:
            d = abs(ex - x) + abs(ey - y)
            if d < best:
                best = d
        return best if best != 10**9 else 10**6

    # Deterministic phase: early expand, later cut off near opponent
    phase = 0
    if turn < 24:
        phase = 0
    elif turn < 48:
        phase = 1
    else:
        phase = 2

    best_move = [0, 0]
    best_val = -10**18
    opp_dist_now = min_manhattan_to_opp(sx, sy)

    for dx, dy in dirs8:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        val = 0.0
        # Territory interaction
        if (nx, ny) in opp_terr:
            val += 120.0  # flipping
        elif (nx, ny) in unclaimed:
            val += 28.0  # expansion
        elif (nx, ny) in self_terr:
            val += 8.0   # consolidation

        # Prefer growing from our frontier
        val += 7.0 * adj4_count(nx, ny, self_terr)

        # Prefer moves that reduce distance to opponent later; early prefer opening space
        d_opp = min_manhattan_to_opp(nx, ny)
        if phase == 0:
            val += 3.0 * (d_opp - opp_dist_now)  # drift away slightly to build
        else:
            val += 6.0 * (opp_dist_now - d_opp)  # go towards opponent

        # Avoid obstacles / tangling
        val += 2.0 * min_dist_to_obstacle(nx, ny)

        # Encourage boundary cutting: if stepping into our territory, don't stall near center too much
        # (territory_sweeper often creates thick bands; cutting needs approach, not wandering)
        if phase >= 1 and (nx, ny) in self_terr:
            val -= 3.0 * (adj4_count(nx, ny, self_terr) >= 3)

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]
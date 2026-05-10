def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    our = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))
    opp = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    un = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def neigh(x, y):
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                yield nx, ny

    best = (-10**18, 0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy  # engine will keep us in place
            dx, dy = 0, 0

        score = 0
        if (nx, ny) in opp:
            score += 1400
        elif (nx, ny) in un:
            score += 900
        elif (nx, ny) in our:
            score += 100
        else:
            score += 10

        # Push toward opponent
        score += 12 * (-(abs(nx - ox) + abs(ny - oy)))

        # If we're on the front, expand faster
        if (nx, ny) in our or (nx, ny) in un or (nx, ny) in opp:
            adj_un = 0
            adj_opp = 0
            adj_obs = 0
            for ax, ay in neigh(nx, ny):
                if (ax, ay) in un:
                    adj_un += 1
                elif (ax, ay) in opp:
                    adj_opp += 1
                if (ax, ay) in obstacles:
                    adj_obs += 1
            score += 70 * adj_un + 130 * adj_opp - 25 * adj_obs

        # Extra tie-breaker: prefer diagonal/forward progress
        score += (dx != 0) * 4 + (dy != 0) * 4

        if (score, -dx, -dy) > (best[0], -best[1], -best[2]):
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]
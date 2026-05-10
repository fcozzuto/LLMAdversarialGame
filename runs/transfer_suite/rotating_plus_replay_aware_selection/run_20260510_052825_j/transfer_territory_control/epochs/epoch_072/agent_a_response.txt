def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    x, y = observation.get("self_position", (0, 0))
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []) if p and len(p) >= 2)
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)
    selfT = set((p[0], p[1]) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    oppT = set((p[0], p[1]) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    ox, oy = observation.get("opponent_position", (x, y))

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]
    deltas.sort()

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def neighbors(nx, ny):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                ax, ay = nx + dx, ny + dy
                if inb(ax, ay):
                    yield ax, ay

    best_move = (0, 0)
    best = -10**18
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0
        if (nx, ny) in unclaimed:
            score += 20
        if (nx, ny) in oppT:
            score += 18

        our_adj = 0
        opp_adj = 0
        un_adj = 0
        for ax, ay in neighbors(nx, ny):
            if (ax, ay) in selfT:
                our_adj += 1
            elif (ax, ay) in oppT:
                opp_adj += 1
            elif (ax, ay) in unclaimed:
                un_adj += 1

        score += 2 * our_adj + 1 * un_adj - 2 * opp_adj

        # Push toward the opponent while expanding into unclaimed/pressure.
        score += -0.1 * (abs(nx - ox) + abs(ny - oy))

        # Avoid getting too far from our territory if it exists.
        if selfT:
            # deterministic approximate: use min manhattan to a few anchor points (corners of our territory)
            min_d = 10**9
            for (ax, ay) in selfT:
                d = abs(nx - ax) + abs(ny - ay)
                if d < min_d:
                    min_d = d
                    if min_d == 0:
                        break
            score += -0.05 * min_d

        if score > best:
            best = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
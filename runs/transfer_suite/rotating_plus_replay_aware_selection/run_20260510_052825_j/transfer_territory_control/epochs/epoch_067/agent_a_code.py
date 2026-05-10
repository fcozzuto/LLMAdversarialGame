def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    x, y = observation.get("self_position", (0, 0))

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2 and p[0] is not None and p[1] is not None:
            obstacles.add((p[0], p[1]))

    unclaimed = set()
    for p in (observation.get("unclaimed_cells") or []):
        if p and len(p) >= 2 and p[0] is not None and p[1] is not None:
            unclaimed.add((p[0], p[1]))

    selfT = set()
    for p in (observation.get("self_territory") or []):
        if p and len(p) >= 2 and p[0] is not None and p[1] is not None:
            selfT.add((p[0], p[1]))

    oppT = set()
    for p in (observation.get("opponent_territory") or []):
        if p and len(p) >= 2 and p[0] is not None and p[1] is not None:
            oppT.add((p[0], p[1]))

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def neighbors4(a, b):
        return ((a - 1, b), (a + 1, b), (a, b - 1), (a, b + 1))

    opp_count = observation.get("opponent_territory_count", len(oppT))
    self_count = observation.get("self_territory_count", len(selfT))
    chase = opp_count > self_count

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        base = 0
        if (nx, ny) in unclaimed:
            base = 50
        elif (nx, ny) in oppT:
            base = 18 if chase else 8
        elif (nx, ny) in selfT:
            base = 8
        else:
            base = 0

        adj_self = 0
        adj_opp = 0
        for ax, ay in neighbors4(nx, ny):
            if (ax, ay) in selfT:
                adj_self += 1
            if (ax, ay) in oppT:
                adj_opp += 1
        base += 6 * adj_self - 7 * adj_opp

        # Small deterministic tie-breaker: prefer moving toward the center of unclaimed, if any
        if unclaimed:
            # nearest unclaimed among at most a few deterministic samples around current move
            candidates = [(nx, ny), (x, ny), (nx, y)]
            mind = 10**9
            for cx, cy in candidates:
                for ux, uy in unclaimed:
                    d = abs(ux - cx) + abs(uy - cy)
                    if d < mind:
                        mind = d
                break
            base -= min(mind, 12)

        # Prefer not to get surrounded when ahead
        if not chase and adj_opp >= 2:
            base -= 15

        # Deterministic ordering
        if (base, -dx, -dy) > (best_score, -best_move[0], -best_move[1]):
            best_score = base
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
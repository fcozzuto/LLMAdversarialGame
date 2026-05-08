def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set(map(tuple, observation.get("obstacles") or []))
    resources = set(map(tuple, observation.get("resources") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    self_t = set(map(tuple, observation.get("self_territory") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    if resources:
        target = min(resources, key=lambda t: (abs(t[0] - cx) + abs(t[1] - cy), abs(t[0] - sx) + abs(t[1] - sy)))
    elif unclaimed:
        target = min(unclaimed, key=lambda t: (abs(t[0] - cx) + abs(t[1] - cy), abs(t[0] - sx) + abs(t[1] - sy)))
    else:
        target = (int(round(cx)), int(round(cy)))

    dxs = (-1, 0, 1, -1, 1, 0, 0)
    dys = (0, -1, 0, 1, 1, -1, 0)  # dummy init to satisfy deterministic list build

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    # Deterministic tiebreak order already fixed.

    def center_gain(x, y):
        return (-(abs(x - cx) + abs(y - cy)))  # higher is better

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Favor: move into opponent territory if reachable; else expand toward a central unclaimed/resource,
    # while lightly contesting near opponent.
    best_move = (0, 0)
    best_sc = -10**18
    opp_adj = set()
    for (x, y) in opp_t:
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                nx, ny = x + ddx, y + ddy
                if inb(nx, ny):
                    opp_adj.add((nx, ny))

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        sc = 0
        sc += 10 * center_gain(nx, ny)
        sc += -3 * manh((nx, ny), target)

        if (nx, ny) in opp_t:
            sc += 250
        elif (nx, ny) in unclaimed:
            sc += 40
        elif (nx, ny) in self_t:
            sc -= 5

        if (nx, ny) in opp_adj:
            sc += 18  # contest/deny center claim expansion

        # Slight bias to reduce distance to opponent to match "territory_center_claim" behavior.
        sc += -0.8 * manh((nx, ny), (ox, oy))

        if sc > best_sc:
            best_sc = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
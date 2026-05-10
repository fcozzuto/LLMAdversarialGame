def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)

    obstacles = set()
    for x, y in (observation.get("obstacles") or []):
        if x is not None and y is not None:
            obstacles.add((int(x), int(y)))

    self_t = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_t = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def mindist_to_opp(x, y):
        if not opp_t:
            return 999
        md = 999
        for ox, oy in opp_t:
            d = abs(x - ox) + abs(y - oy)
            if d < md:
                md = d
        return md

    def frontier_score(x, y):
        if (x, y) in self_t:
            return 0
        # prefer cells adjacent to our territory and unclaimed
        adj_self = False
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            if (x + dx, y + dy) in self_t:
                adj_self = True
                break
        if (x, y) in unclaimed and adj_self:
            return 6
        if (x, y) in unclaimed:
            return 3
        if (x, y) in opp_t:
            # allow flipping if close to opp
            return 2
        return -2

    best = None
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        val = 0
        md = mindist_to_opp(nx, ny)
        val += md * 5  # keep away from opponent when possible

        val += frontier_score(nx, ny)

        if (nx, ny) in self_t:
            val += 1  # mild preference to hold territory

        # if forcing toward opponent territory, prefer immediate flip area
        if (nx, ny) in opp_t:
            val += (10 - md) * 2

        # deterministic tie-break: fixed move order already ensures stable selection
        if val > best_val:
            best_val = val
            best = (nx - sx, ny - sy)

    return [int(best[0]), int(best[1])]
def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in (observation.get("obstacles") or []):
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    self_t = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_t = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    nbrs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def frontier_score(x, y):
        c = 0
        for dx, dy in nbrs:
            nx, ny = x + dx, y + dy
            if (nx, ny) in opp_t:
                c += 1
        return c

    best = (0, 0)
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            nx, ny, dx, dy = sx, sy, 0, 0

        v = 0
        if (nx, ny) in opp_t:
            v += 700
            v += 80 * frontier_score(nx, ny)
            v -= 35 * (abs(nx - ox) + abs(ny - oy))
        elif (nx, ny) in unclaimed:
            v += 240
            v += 25 * frontier_score(nx, ny)
            v -= 15 * (abs(nx - ox) + abs(ny - oy))
        elif (nx, ny) in self_t:
            v += 40
            v -= 10 * frontier_score(nx, ny)

        # Prefer progress toward the densest opponent frontier when not directly taking it
        if (nx, ny) not in opp_t:
            if opp_t:
                tx, ty = next(iter(opp_t))
                dcur = abs(sx - tx) + abs(sy - ty)
                dnew = abs(nx - tx) + abs(ny - ty)
                v += 30 * (dcur - dnew)

        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]
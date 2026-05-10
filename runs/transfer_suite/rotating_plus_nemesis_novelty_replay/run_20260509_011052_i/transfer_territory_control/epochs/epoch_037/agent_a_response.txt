def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))

    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []))
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []))
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    dirs8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj_cnt(x, y, S):
        c = 0
        for dx, dy in dirs4:
            nx, ny = x + dx, y + dy
            if (nx, ny) in S:
                c += 1
        return c

    def dist_to_op(x, y):
        return abs(ox - x) + abs(oy - y)

    best = (float("-inf"), 0, 0)
    for dx, dy in dirs8:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        a_self = adj_cnt(nx, ny, self_terr)
        a_opp = adj_cnt(nx, ny, opp_terr)
        d = dist_to_op(nx, ny)

        if (nx, ny) in unclaimed:
            base = 3.2
        elif (nx, ny) in self_terr:
            base = 1.0
        elif (nx, ny) in opp_terr:
            base = -2.6 + 0.7 * a_self - 0.4 * a_opp
        else:
            base = 0.6  # should be rare

        score = base + 0.55 * a_self - 0.25 * a_opp - 0.12 * d
        if score > best[0]:
            best = (score, dx, dy)
        elif score == best[0]:
            if (dx, dy) < (best[1], best[2]):
                best = (score, dx, dy)

    return [int(best[1]), int(best[2])]
def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []))
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []))
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def count_neighbors(x, y, S):
        c = 0
        for dx, dy in dirs4:
            nx, ny = x + dx, y + dy
            if (nx, ny) in S:
                c += 1
        return c

    def cell_value(x, y):
        if (x, y) in obstacles:
            return -10**9
        d_op = abs(ox - x) + abs(oy - y)
        v = 0
        if (x, y) in opp_terr:
            v += 8  # flipping on entry
        elif (x, y) in self_terr:
            v += 1
        elif (x, y) in unclaimed:
            v += 4  # expand territory
        v += 0.35 * d_op  # resist opponent center pressure
        v += 0.75 * count_neighbors(x, y, unclaimed)  # grab frontier
        v -= 0.6 * count_neighbors(x, y, opp_terr)  # avoid getting locked in their blob
        return v

    best = [0, 0]
    best_v = -10**18
    # Tie-break deterministically: prefer not-stay, then lexicographic dx,dy
    prefer_moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        prefer_moves.append((0 if (dx == 0 and dy == 0) else -1, dx, dy))
    for _, dx, dy in sorted(prefer_moves, key=lambda t: (t[0], t[1], t[2])):
        nx, ny = sx + dx, sy + dy
        v = cell_value(nx, ny)
        if v > best_v:
            best_v = v
            best = [dx, dy]
    return [int(best[0]), int(best[1])]
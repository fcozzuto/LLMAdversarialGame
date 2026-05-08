def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        obstacles.add((int(p[0]), int(p[1])))

    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []))
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []))
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []))
    resources = set((int(p[0]), int(p[1])) for p in (observation.get("resources") or []))

    def manh(x, y):
        return abs(x - ox) + abs(y - oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_value(x, y):
        if (x, y) in obstacles:
            return -10**9
        if (x, y) in resources:
            return 1200 - 0.25 * manh(x, y)
        if (x, y) in opp_terr:
            # flipping on entry is True
            return 1100 - 0.35 * manh(x, y)
        if (x, y) in unclaimed:
            return 420 - 0.15 * manh(x, y)
        if (x, y) in self_terr:
            return 140 - 0.05 * manh(x, y)
        # neutral-ish
        return 180 - 0.1 * manh(x, y)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (-10**18, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # small tie-breakers: move toward opponent initially, but avoid stepping away too much
        v = cell_value(nx, ny) + 0.02 * (manh(sx, sy) - manh(nx, ny))
        if v > best[0] or (v == best[0] and (dx, dy) < (best[1], best[2])):
            best = (v, dx, dy)

    if best[0] < -10**8:
        return [0, 0]
    return [int(best[1]), int(best[2])]
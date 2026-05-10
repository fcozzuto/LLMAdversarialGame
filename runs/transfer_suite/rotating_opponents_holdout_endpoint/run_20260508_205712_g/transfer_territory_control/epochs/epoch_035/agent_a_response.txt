def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)

    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles") or []))
    self_terr = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_terr = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if opp_terr:
        ox = sum(x for x, _ in opp_terr) / float(len(opp_terr))
        oy = sum(y for _, y in opp_terr) / float(len(opp_terr))
    else:
        ox, oy = (w - 1) / 2.0, (h - 1) / 2.0

    def dist2_to_centroid(x, y):
        dx = x - ox
        dy = y - oy
        return dx * dx + dy * dy

    targets = []
    if unclaimed:
        targets = list(unclaimed)
    if opp_terr:
        targets += [p for p in opp_terr if p not in unclaimed]

    best = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0

        if targets:
            nd = min(abs(nx - tx) + abs(ny - ty) for tx, ty in targets)
        else:
            nd = abs(nx - (w - 1)) + abs(ny - (h - 1))

        val = 0
        if (nx, ny) in unclaimed:
            val += 5.0
        if (nx, ny) in opp_terr:
            val += 3.5
        if (nx, ny) in self_terr:
            val += 1.0

        val += 1.2 / (1.0 + nd)
        val -= 0.002 * dist2_to_centroid(nx, ny)
        if dx == 0 and dy == 0:
            val -= 0.35

        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]
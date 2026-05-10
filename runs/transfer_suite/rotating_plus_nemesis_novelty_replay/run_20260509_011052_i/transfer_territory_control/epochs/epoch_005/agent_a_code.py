def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position", (sx, sy))
    ox, oy = int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory", []) or []))
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    unclaimed_list = list(unclaimed)
    if unclaimed_list:
        edge_unclaimed = [c for c in unclaimed_list if c[0] in (0, w - 1) or c[1] in (0, h - 1)]
    else:
        edge_unclaimed = []

    self_count = int(observation.get("self_territory_count", len(self_terr)))
    opp_count = int(observation.get("opponent_territory_count", len(opp_terr)))
    aggressive = 1 if opp_count >= self_count else 0

    if aggressive and opp_terr:
        targets = list(opp_terr)
        if unclaimed_list:
            targets = (edge_unclaimed if edge_unclaimed else unclaimed_list) + targets
    else:
        targets = (edge_unclaimed if edge_unclaimed else unclaimed_list) or list(opp_terr)

    if not targets:
        return [0, 0]

    def mdist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    tx, ty = min(targets, key=lambda c: (mdist(sx, sy, c[0], c[1]), c[0], c[1]))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        val = 0
        if (nx, ny) in opp_terr:
            val += 1200
        if (nx, ny) in unclaimed:
            val += 120
            if nx in (0, w - 1) or ny in (0, h - 1):
                val += 25
        if (nx, ny) in self_terr:
            val += 15

        d_to_target = mdist(nx, ny, tx, ty)
        val += 30 - d_to_target

        d_to_opp = mdist(nx, ny, ox, oy)
        val -= 2 * d_to_opp * aggressive

        if val > best_val:
            best_val = val
            best_move = (dx, dy)
        elif val == best_val:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    ax, ay = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    self_terr = observation.get("self_territory") or []
    opp_terr = observation.get("opponent_territory") or []
    unclaimed = observation.get("unclaimed_cells") or []
    obstacles = observation.get("obstacles") or []

    def toset(lst):
        s = set()
        for p in lst:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    uset = toset(self_terr)
    oset = toset(opp_terr)
    ucell = toset(unclaimed)
    obset = toset(obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = -10**18
    bestmv = [0, 0]

    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obset:
            continue

        md_opp = abs(nx - ox) + abs(ny - oy)
        md_self = abs(nx - ax) + abs(ny - ay)

        val = -md_self
        if (nx, ny) in ucell:
            val += 6000
        if (nx, ny) in oset:
            val += 2400 + 6 * md_opp  # flip but prefer pushing away as edge-claimer
        if (nx, ny) in uset:
            val += 200  # consolidation

        # Frontier preference: prefer cells adjacent to unclaimed to keep expanding deterministically
        adj_unclaimed = 0
        for sx, sy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            xx, yy = nx + sx, ny + sy
            if inb(xx, yy) and (xx, yy) in ucell:
                adj_unclaimed += 1
        val += 150 * adj_unclaimed

        # Anti-trap: avoid stepping into tight obstacle corners by penalizing blocked neighbors
        blocked = 0
        for sx, sy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            xx, yy = nx + sx, ny + sy
            if not inb(xx, yy) or (xx, yy) in obset:
                blocked += 1
        val -= 20 * blocked

        if val > best:
            best = val
            bestmv = [dx, dy]

    return [int(bestmv[0]), int(bestmv[1])]
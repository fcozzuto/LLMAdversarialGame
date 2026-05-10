def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    ax, ay = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    self_terr = observation.get("self_territory") or []
    opp_terr = observation.get("opponent_territory") or []
    unclaimed = observation.get("unclaimed_cells") or []
    obstacles = observation.get("obstacles") or []

    def toset(lst):
        s = set()
        for p in lst:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                s.add((x, y))
        return s

    uset = toset(self_terr)
    oset = toset(opp_terr)
    ucell = toset(unclaimed)
    obset = toset(obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    unbehind = int(observation.get("self_territory_count", len(uset))) < int(observation.get("opponent_territory_count", len(oset)))
    centerx, centery = (w - 1) / 2.0, (h - 1) / 2.0

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    bestv = -10**18
    oppdist_now = man(ax, ay, ox, oy)

    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obset:
            continue

        val = 0
        if (nx, ny) in ucell:
            val += 2200
        elif (nx, ny) in oset:
            val += 1600
            val += 40 * (oppdist_now - man(nx, ny, ox, oy))  # prefer moves that bring us closer to opponent only when capturing
        elif (nx, ny) in uset:
            val += 180
        else:
            val += 60  # stepping onto empty/unlisted cells still helps momentum

        # drive toward center while not suicidal if far behind capturing isn't possible
        val += -8 * ((nx - centerx) ** 2 + (ny - centery) ** 2)

        # if we're behind, be more aggressive; otherwise keep some distance from opponent unless it’s a capture
        if (nx, ny) not in oset:
            if unbehind:
                val += 8 * (man(nx, ny, ox, oy) - oppdist_now)
            else:
                val += -12 * (oppdist_now - man(nx, ny, ox, oy))

        # mild obstacle-adjacency penalty (deterministic)
        for ddx, ddy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            axx, ayy = nx + ddx, ny + ddy
            if (axx, ayy) in obset:
                val -= 25

        if val > bestv:
            bestv = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best
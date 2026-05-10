def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    x, y = observation.get("self_position") or [0, 0]
    x, y = int(x), int(y)

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) == 2:
                s.add((int(p[0]), int(p[1])))
        return s

    blocks = to_set("obstacles")
    unclaimed = to_set("unclaimed_cells")
    opp_terr = to_set("opponent_territory")
    self_terr = to_set("self_territory")

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = [0, 0]
    best_sc = -10**9

    def inb(px, py): return 0 <= px < w and 0 <= py < h
    def adj8(px, py):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = px + dx, py + dy
                if inb(nx, ny):
                    yield nx, ny

    opp_front = []
    if unclaimed:
        for c in unclaimed:
            if any((nx, ny) in opp_terr for nx, ny in adj8(c[0], c[1])):
                opp_front.append(c)

    if not opp_front:
        for c in unclaimed:
            k = 0
            for nx, ny in adj8(c[0], c[1]):
                if (nx, ny) in opp_terr:
                    k += 1
            if k >= 2:
                opp_front.append(c)

    if not opp_front and opp_terr:
        # Aim near opponent territory if no frontier exists
        opp_front = [next(iter(opp_terr))]

    target = None
    if opp_front:
        ox = min(opp_front, key=lambda c: abs(c[0] - x) + abs(c[1] - y))
        target = ox

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in blocks:
            continue
        sc = 0
        if (nx, ny) in opp_terr:
            sc += 120
        if (nx, ny) in unclaimed:
            sc += 60
        if (nx, ny) in self_terr:
            sc += 5

        # Frontier push: prioritize cells adjacent to opponent territory
        adj_opp = 0
        for ax, ay in adj8(nx, ny):
            if (ax, ay) in opp_terr:
                adj_opp += 1
        sc += 10 * adj_opp

        # Distance to target (deterministic, greedy)
        if target is not None:
            sc += -2 * (abs(nx - target[0]) + abs(ny - target[1]))

        # Mild preference to avoid sticking if target exists
        if dx == 0 and dy == 0 and target is not None:
            sc -= 8

        if sc > best_sc or (sc == best_sc and (dx, dy) == tuple(best)):
            best_sc = sc
            best = [dx, dy]

    return best
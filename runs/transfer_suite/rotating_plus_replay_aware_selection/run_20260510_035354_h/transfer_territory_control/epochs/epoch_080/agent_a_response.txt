def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
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
                s.add((int(p[0]), int(p[1])))
        return s

    uset = toset(self_terr)
    oset = toset(opp_terr)
    ucell = toset(unclaimed)
    obset = toset(obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    opp_adj = set()
    for (x, y) in oset:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obset:
                    opp_adj.add((nx, ny))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    bestv = -10**18

    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obset:
            continue

        # Primary objective: steal/claim near opponent edge; otherwise claim open space.
        v = 0
        if (nx, ny) in ucell:
            v += 12000
        if (nx, ny) in oset:
            v += 9000
        if (nx, ny) in opp_adj and (nx, ny) not in uset:
            v += 4500
        if (nx, ny) in uset:
            v -= 1200  # discourage wasting turns on already-owned cells

        # Secondary: move to reduce distance to opponent-controlled territory when contesting.
        d_now = abs(ax - ox) + abs(ay - oy)
        d_next = abs(nx - ox) + abs(ny - oy)
        v += (d_now - d_next) * 40

        # Tertiary: prefer moves that reduce distance to nearest unclaimed (if any).
        if ucell:
            # small exact check over a capped list for determinism and speed
            targets = list(ucell)
            if len(targets) > 25:
                targets = sorted(targets)[:25]
            md = 10**9
            for tx, ty in targets:
                d = abs(tx - nx) + abs(ty - ny)
                if d < md:
                    md = d
            v += -md * 8

        # Avoid clustering on exact opponent position corner-cases
        if (nx, ny) == (ox, oy):
            v -= 300

        if v > bestv:
            bestv = v
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]
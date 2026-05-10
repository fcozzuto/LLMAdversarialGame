def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    x, y = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]

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

    def inb(px, py): return 0 <= px < w and 0 <= py < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_move = [0, 0]
    best_sc = -10**18

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in blocks:
            continue

        sc = 0
        if (nx, ny) in opp_terr:
            sc += 8
        if (nx, ny) in unclaimed:
            sc += 5
        if (nx, ny) in self_terr:
            sc += 2

        # Pressure: prefer cells near opponent territory, but also avoid being too exposed.
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                px, py = nx + ax, ny + ay
                if inb(px, py):
                    if (px, py) in opp_terr:
                        sc += 3
                    if (px, py) in self_terr:
                        sc += 1
                    if (px, py) in blocks:
                        sc -= 1

        dist_opp = abs(nx - ox) + abs(ny - oy)
        sc += 6 - dist_opp  # deterministic chase of opponent expansion front

        if sc > best_sc:
            best_sc = sc
            best_move = [dx, dy]

    return best_move
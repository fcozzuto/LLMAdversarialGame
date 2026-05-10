def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            obstacles.add((x, y))

    self_terr = set()
    for c in (observation.get("self_territory") or []):
        if c and len(c) >= 2:
            self_terr.add((int(c[0]), int(c[1])))

    opp_terr = set()
    for c in (observation.get("opponent_territory") or []):
        if c and len(c) >= 2:
            opp_terr.add((int(c[0]), int(c[1])))

    unclaimed = set()
    for c in (observation.get("unclaimed_cells") or []):
        if c and len(c) >= 2:
            unclaimed.add((int(c[0]), int(c[1])))

    opp_pos = observation.get("opponent_position", (None, None))
    ox, oy = opp_pos if isinstance(opp_pos, (list, tuple)) and len(opp_pos) >= 2 else (None, None)
    ox, oy = int(ox) if ox is not None else None, int(oy) if oy is not None else None

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    unclaimed_list = list(unclaimed)
    opp_list = list(opp_terr)

    def mindist(cands, x, y):
        if not cands:
            return 10**9
        md = 10**9
        for cx, cy in cands:
            d = abs(cx - x) + abs(cy - y)
            if d < md:
                md = d
        return md

    best = None
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if (nx, ny) in opp_terr:
            v = 50
            v += 5 * (0 if ox is None else -((abs(ox - nx) + abs(oy - ny)) / 10))
        elif (nx, ny) in unclaimed:
            v = 15
        elif (nx, ny) in self_terr:
            v = 8
        else:
            v = 4

        du = mindist(unclaimed_list, nx, ny)
        do = mindist(opp_list, nx, ny)

        v += -du * 1.2
        v += -do * 0.6

        if best is None or v > bestv:
            bestv = v
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]
def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    self_terr = set()
    for p in observation.get("self_territory") or []:
        if p and len(p) >= 2:
            self_terr.add((int(p[0]), int(p[1])))
    opp_terr = set()
    for p in observation.get("opponent_territory") or []:
        if p and len(p) >= 2:
            opp_terr.add((int(p[0]), int(p[1])))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                unclaimed.append((x, y))
    if not unclaimed:
        unclaimed = [(sx, sy)]

    opp_adj = set()
    for (x, y) in list(opp_terr):
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)):
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in opp_terr:
                opp_adj.add((nx, ny))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best_val = -10**18
    best_move = [0, 0]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        d_unc = 10**9
        for ux, uy in unclaimed:
            t = abs(ux - nx) + abs(uy - ny)
            if t < d_unc:
                d_unc = t

        val = -d_unc
        if (nx, ny) in opp_terr:
            val += 120
        if (nx, ny) in unclaimed:
            val += 45
        if (nx, ny) in self_terr:
            val += 8
        if (nx, ny) in opp_adj:
            val += 22
        val += 0.5 * (abs(nx - ox) + abs(ny - oy))  # keep pressure distance-biased

        if val > best_val or (val == best_val and (dx, dy) < tuple(best_move)):
            best_val = val
            best_move = [dx, dy]

    return best_move
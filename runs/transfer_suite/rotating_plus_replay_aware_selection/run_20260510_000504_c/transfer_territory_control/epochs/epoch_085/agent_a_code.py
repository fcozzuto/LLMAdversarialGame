def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cell_gain(nx, ny):
        if (nx, ny) in self_terr:
            base = 0
        elif (nx, ny) in unclaimed:
            base = 1
        elif (nx, ny) in opp_terr:
            base = 1  # flipping on entry
        else:
            base = 0
        if (nx, ny) in obstacles or not inb(nx, ny):
            return -10**6
        return base

    # Heuristic: maximize immediate territory gain; then maximize adjacency to unclaimed,
    # and reduce distance to nearest unclaimed cell (to keep pushing), while avoiding
    # wandering into opponent-only areas if no gain.
    targets = list(unclaimed) if unclaimed else list(opp_terr)
    t0 = targets[0] if targets else None

    best = (-10**9, (0, 0))
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        g = cell_gain(nx, ny)

        adj_un = 0
        adj_opp = 0
        adj_self = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                xx, yy = nx + ax, ny + ay
                if not inb(xx, yy) or (xx, yy) in obstacles:
                    continue
                if (xx, yy) in unclaimed:
                    adj_un += 1
                elif (xx, yy) in opp_terr:
                    adj_opp += 1
                elif (xx, yy) in self_terr:
                    adj_self += 1

        if t0 is not None:
            md = abs(t0[0] - nx) + abs(t0[1] - ny)
            # also consider a couple more targets deterministically
            md2 = 10**9
            for k in (1, 2, 3):
                if k < len(targets):
                    tt = targets[k]
                    d = abs(tt[0] - nx) + abs(tt[1] - ny)
                    if d < md2:
                        md2 = d
            md = md if md2 == 10**9 else (md if md < md2 else md2)
        else:
            md = 0

        toward = -md  # smaller distance => larger value
        opp_penalty = 0
        if g == 0 and (nx, ny) in opp_terr:
            opp_penalty = 1.5  # only enter opponent if it yields immediate gain
        if (dx, dy) == (0, 0):
            toward -= 0.75  # prefer moving

        score = g * 5.0 + adj_un * 1.2 + (adj_opp - adj_self * 0.3) * 0.4 + toward * 0.12 - opp_penalty
        if score > best[0]:
            best = (score, (dx, dy))

    return [int(best[1][0]), int(best[1][1])]
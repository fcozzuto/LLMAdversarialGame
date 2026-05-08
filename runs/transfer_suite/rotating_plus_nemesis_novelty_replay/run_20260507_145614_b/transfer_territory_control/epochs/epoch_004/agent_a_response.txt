def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    self_t = set()
    for p in observation.get("self_territory", []) or []:
        if p and len(p) >= 2:
            self_t.add((p[0], p[1]))
    opp_t = set()
    for p in observation.get("opponent_territory", []) or []:
        if p and len(p) >= 2:
            opp_t.add((p[0], p[1]))

    unclaimed = set()
    for p in observation.get("unclaimed_cells", []) or []:
        if p and len(p) >= 2:
            unclaimed.add((p[0], p[1]))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def score_cell(x, y):
        if (x, y) in obstacles or not inb(x, y):
            return -10**9
        if (x, y) in self_t:
            base = 1.0
        elif (x, y) in opp_t:
            base = 8.0  # capturing opponent control on entry
        elif (x, y) in unclaimed:
            base = 5.0  # expanding into neutral
        else:
            base = 2.0  # safety/unknown

        # prefer advancing toward opponent and toward available unclaimed
        dist_to_opp = abs(x - ox) + abs(y - oy)
        adv = 7.0 / (1.0 + dist_to_opp)

        # prefer touching our territory (stable growth) but don't ignore capture
        adj_self = 0
        adj_opp = 0
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                if (nx, ny) in self_t:
                    adj_self += 1
                elif (nx, ny) in opp_t:
                    adj_opp += 1
        touch = 0.8 * adj_self + 0.6 * adj_opp

        # avoid moving into a tight choke when opponent is adjacent (gives them free claim lines)
        adj_to_opp_pos = max(abs(x - ox), abs(y - oy)) <= 1 and (x, y) not in self_t
        risk = -2.5 if adj_to_opp_pos and (x, y) not in opp_t else 0.0

        return base + adv + touch + risk

    best = (-10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        sc = score_cell(nx, ny)
        if sc > best[0]:
            best = (sc, dx, dy)

    return [int(best[1]), int(best[2])]
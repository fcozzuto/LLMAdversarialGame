def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    oxp = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(oxp[0]), int(oxp[1])

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y):
                blocked.add((x, y))

    selfT = set()
    for t in observation.get("self_territory") or []:
        if t is not None and len(t) >= 2:
            selfT.add((int(t[0]), int(t[1])))

    oppT = set()
    for t in observation.get("opponent_territory") or []:
        if t is not None and len(t) >= 2:
            oppT.add((int(t[0]), int(t[1])))

    unclaimed = set()
    for t in observation.get("unclaimed_cells") or []:
        if t is not None and len(t) >= 2:
            unclaimed.add((int(t[0]), int(t[1])))

    resources = set()
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            resources.add((int(r[0]), int(r[1])))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    def neighbors(x, y):
        for dx, dy in dirs:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if inside(nx, ny):
                yield nx, ny

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in blocked:
            continue

        into_opp = (nx, ny) in oppT
        into_self = (nx, ny) in selfT
        into_uncl = (nx, ny) in unclaimed
        into_res = (nx, ny) in resources

        score = 0
        score += 120 if into_opp else 0
        score += 30 if into_uncl else 0
        score += 5 if into_res else 0
        score -= 3 if into_self else 0

        if into_uncl or into_opp:
            adj_uncl = 0
            adj_opp = 0
            adj_self = 0
            for ax, ay in neighbors(nx, ny):
                if (ax, ay) in unclaimed:
                    adj_uncl += 1
                if (ax, ay) in oppT:
                    adj_opp += 1
                if (ax, ay) in selfT:
                    adj_self += 1
            score += 4 * adj_uncl + 8 * adj_opp + 2 * adj_self

        score += -0.5 * (abs(nx - ox) + abs(ny - oy))  # pressure opponent
        score += 0.01 * ((nx - (w - 1) / 2.0) ** 2 + (ny - (h - 1) / 2.0) ** 2)  # slight corner preference

        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
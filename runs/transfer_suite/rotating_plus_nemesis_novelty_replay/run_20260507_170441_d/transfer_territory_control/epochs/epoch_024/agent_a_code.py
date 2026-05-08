def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                unclaimed.add((x, y))
        except:
            pass

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 0)]
    opp_terr = set()
    for p in observation.get("opponent_territory") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                opp_terr.add((x, y))
        except:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    unclaimed_list = sorted(unclaimed)
    if unclaimed_list:
        nearest_target = min(unclaimed_list, key=lambda t: (abs(t[0] - ox) + abs(t[1] - oy), t[0], t[1]))
    else:
        nearest_target = None

    best = None
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        score = 0
        if (nx, ny) in unclaimed:
            score += 1000
        if (nx, ny) in opp_terr:
            score -= 30
        if nearest_target is not None:
            score += -2 * (abs(nx - nearest_target[0]) + abs(ny - nearest_target[1]))
        score += -abs(nx - ox) - abs(ny - oy)
        score += -2 * (dx == 0 and dy == 0)

        if best is None or score > best_score or (score == best_score and (dx, dy) < best):
            best = (dx, dy)
            best_score = score

    if best is None:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in blocked:
                return [dx, dy]
        return [0, 0]

    return [best[0], best[1]]
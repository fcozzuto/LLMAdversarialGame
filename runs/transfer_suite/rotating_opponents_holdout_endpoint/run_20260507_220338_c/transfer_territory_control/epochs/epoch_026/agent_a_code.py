def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles") or []))
    un = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))
    my = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))

    ox, oy = observation.get("opponent_position") or (sx, sy)
    ox, oy = int(ox), int(oy)

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    un_best = None
    if un:
        min_d = 10**9
        for ux, uy in un:
            d = abs(ux - sx) + abs(uy - sy)
            if d < min_d or (d == min_d and (ux, uy) < un_best):
                min_d = d
                un_best = (ux, uy)

    opp_best = None
    if opp:
        min_d = 10**9
        for px, py in opp:
            d = abs(px - sx) + abs(py - sy)
            if d < min_d or (d == min_d and (px, py) < opp_best):
                min_d = d
                opp_best = (px, py)

    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        score = 0
        if (nx, ny) in un:
            score += 1000
        if (nx, ny) in my:
            score += 20
        if (nx, ny) in opp:
            score += 200

        if un_best is not None:
            score += 30 - (abs(un_best[0] - nx) + abs(un_best[1] - ny))
        else:
            score += - (abs(ox - nx) + abs(oy - ny))

        if opp_best is not None:
            score += 5 - (abs(opp_best[0] - nx) + abs(opp_best[1] - ny))

        score -= 2 * (abs(dx) + abs(dy) == 0)
        if best is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]
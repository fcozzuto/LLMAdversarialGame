def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def neighbors8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx != 0 or dy != 0:
                    nx, ny = x + dx, y + dy
                    if inside(nx, ny):
                        yield nx, ny

    if not inside(sx, sy):
        sx, sy = 0, 0

    target = None
    best_td = None
    for ux, uy in unclaimed:
        if any((ax, ay) in opp_t for ax, ay in neighbors8(ux, uy)):
            d = abs(ux - sx) + abs(uy - sy)
            if best_td is None or d < best_td or (d == best_td and (ux, uy) < target):
                best_td = d
                target = (ux, uy)
    if target is None and unclaimed:
        for ux, uy in unclaimed:
            d = abs(ux - sx) + abs(uy - sy)
            if best_td is None or d < best_td or (d == best_td and (ux, uy) < target):
                best_td = d
                target = (ux, uy)

    def count_in(cset, x, y):
        k = 0
        for ax, ay in neighbors8(x, y):
            if (ax, ay) in cset:
                k += 1
        return k

    move_options = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in move_options:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0.0
        if (nx, ny) in opp_t:
            score += 12.0
        elif (nx, ny) in unclaimed:
            score += 5.0
        elif (nx, ny) in self_t:
            score += 1.0

        opp_adj = count_in(opp_t, nx, ny)
        if opp_adj:
            score += 2.5 * opp_adj

        unc_adj = count_in(unclaimed, nx, ny)
        if unc_adj:
            score += 0.6 * unc_adj

        if target is not None:
            score -= 0.12 * (abs(nx - target[0]) + abs(ny - target[1]))

        score -= 0.08 * (dx == 0 and dy == 0)  # slight preference to move

        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
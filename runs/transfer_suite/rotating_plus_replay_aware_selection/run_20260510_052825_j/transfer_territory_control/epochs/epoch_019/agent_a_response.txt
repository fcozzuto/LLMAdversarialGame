def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def mindist_to_set(px, py, S):
        best = None
        for sx, sy in S:
            d = abs(sx - px) + abs(sy - py)
            if best is None or d < best:
                best = d
        return best if best is not None else 999

    def count_unclaimed_neighbors(px, py):
        c = 0
        for dx, dy in dirs:
            nx, ny = px + dx, py + dy
            if inb(nx, ny) and (nx, ny) in unclaimed:
                c += 1
        return c

    nearest_un = None
    if unclaimed:
        for ux, uy in unclaimed:
            d = abs(ux - x) + abs(uy - y)
            if nearest_un is None or d < nearest_un[0]:
                nearest_un = (d, (ux, uy))
    nearest_opp = None
    if oppT:
        for ox, oy in oppT:
            d = abs(ox - x) + abs(oy - y)
            if nearest_opp is None or d < nearest_opp[0]:
                nearest_opp = (d, (ox, oy))

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue

        score = 0.0
        if (nx, ny) in unclaimed:
            score += 3.4
        if (nx, ny) in oppT:
            score += 4.2

        score += 0.6 * count_unclaimed_neighbors(nx, ny)

        if oppT:
            score += -0.12 * mindist_to_set(nx, ny, oppT)
        if unclaimed:
            score += -0.06 * mindist_to_set(nx, ny, unclaimed)

        score += -0.03 * (abs(nx - cx) + abs(ny - cy))

        # if we're inside opponent pressure, prioritize securing directly
        if oppT:
            do = mindist_to_set(x, y, oppT)
            if do <= 2 and (nx, ny) in selfT:
                score += 0.15

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
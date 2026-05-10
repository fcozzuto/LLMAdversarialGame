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

    def count_unclaimed_neighbors(px, py):
        c = 0
        for dx, dy in dirs:
            nx, ny = px + dx, py + dy
            if inb(nx, ny) and (nx, ny) in unclaimed:
                c += 1
        return c

    def nearest_un_dist(px, py):
        best = None
        for ux, uy in unclaimed:
            d = abs(ux - px) + abs(uy - py)
            if best is None or d < best:
                best = d
        return best if best is not None else 999

    opp_cent = None
    if oppT:
        sx = sy = 0
        n = len(oppT)
        for px, py in oppT:
            sx += px
            sy += py
        opp_cent = (sx / n, sy / n)

    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        score = 0

        if (nx, ny) in oppT:
            score += 120
            if opp_cent is not None:
                score -= 0.2 * (abs(nx - opp_cent[0]) + abs(ny - opp_cent[1]))
        elif (nx, ny) in unclaimed:
            score += 26
            score += 2.5 * count_unclaimed_neighbors(nx, ny)
            score -= 0.35 * nearest_un_dist(nx, ny)
        elif (nx, ny) in selfT:
            score += 6
        else:
            score += 1  # other valid cell, likely edge

        score += 0.01 * (-(abs(nx - cx) + abs(ny - cy)))  # mild center bias
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move
def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def neighbor_unclaimed(px, py):
        c = 0
        for dx, dy in dirs:
            nx, ny = px + dx, py + dy
            if inb(nx, ny) and (nx, ny) in unclaimed:
                c += 1
        return c

    def cell_value(px, py):
        if (px, py) in selfT:
            return 5
        if (px, py) in oppT:
            return 60
        if (px, py) in unclaimed:
            return 25
        return 0

    opp_cent = None
    if oppT:
        sx = 0
        sy = 0
        for px, py in oppT:
            sx += px
            sy += py
        opp_cent = (sx / len(oppT), sy / len(oppT))

    best = None
    best_s = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            nx, ny = x, y
            dx, dy = 0, 0
        s = 0
        s += cell_value(nx, ny)
        s += 3 * neighbor_unclaimed(nx, ny)
        if opp_cent is not None:
            s -= 0.6 * (abs(nx - opp_cent[0]) + abs(ny - opp_cent[1]))
        # Encourage reaching boundary expansions: cells near unclaimed get priority
        if (nx, ny) in selfT:
            s += 0.5 * neighbor_unclaimed(nx, ny)
        if best is None or s > best_s:
            best_s = s
            best = [dx, dy]
    return [int(best[0]), int(best[1])]
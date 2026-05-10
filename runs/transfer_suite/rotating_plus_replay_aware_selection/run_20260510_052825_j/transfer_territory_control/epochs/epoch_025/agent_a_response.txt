def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Opponent centroid (deterministic)
    if oppT:
        sx = sy = 0
        n = len(oppT)
        for px, py in oppT:
            sx += px
            sy += py
        ocx = sx / n
        ocy = sy / n
    else:
        ocx, ocy = w - 1, h - 1

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def count_unclaimed_neighbors(px, py):
        c = 0
        for ddx, ddy in dirs:
            nx2, ny2 = px + ddx, py + ddy
            if inb(nx2, ny2) and (nx2, ny2) in unclaimed:
                c += 1
        return c

    best_dx, best_dy, best_score = 0, 0, -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            nx, ny = x, y  # engine keeps in place

        dself = abs(nx - x) + abs(ny - y)
        dtop = abs(nx - ocx) + abs(ny - ocy)

        cell_unclaimed = (nx, ny) in unclaimed
        cell_opp = (nx, ny) in oppT
        cell_self = (nx, ny) in selfT
        adj_unclaimed = count_unclaimed_neighbors(nx, ny)

        # Encourage claiming expansion; only go into opponent territory when it is actionable.
        score = 0
        if cell_self:
            score += 0.2 + 0.1 * adj_unclaimed - 0.05 * dtop
        elif cell_unclaimed:
            score += 3.0 * adj_unclaimed - 0.08 * dtop - 0.02 * dself
        elif cell_opp:
            score += 6.0 + 0.6 * adj_unclaimed - 0.15 * dtop - 0.03 * dself
        else:
            score += 0.1 * adj_unclaimed - 0.10 * dtop - 0.02 * dself

        if score > best_score:
            best_score, best_dx, best_dy = score, dx, dy

    return [int(best_dx), int(best_dy)]
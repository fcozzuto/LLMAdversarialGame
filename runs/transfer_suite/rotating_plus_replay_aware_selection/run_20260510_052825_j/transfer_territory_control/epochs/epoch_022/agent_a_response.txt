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

    def neighbor_unclaimed_gain(px, py):
        c = 0
        for ddx, ddy in dirs:
            nx, ny = px + ddx, py + ddy
            if inb(nx, ny) and (nx, ny) in unclaimed:
                c += 1
        return c

    best = (None, -10**18)
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if (not (0 <= nx < w and 0 <= ny < h)) or (nx, ny) in obstacles:
            nx, ny = x, y  # engine keeps in place on invalid move

        man_to_opp = abs(nx - ocx) + abs(ny - ocy)

        score = 0
        if (nx, ny) in oppT:
            score += 14
        elif (nx, ny) in unclaimed:
            score += 7
        elif (nx, ny) in selfT:
            score -= 4
        else:
            score -= 1

        score += 2 * neighbor_unclaimed_gain(nx, ny)
        score += -0.05 * man_to_opp  # slight pull toward opponent side

        # tie-break deterministically: prefer moves with smaller dx, then smaller dy, then prefer staying
        if score > best[1]:
            best = ((dx, dy), score)
        elif score == best[1]:
            cand = (dx, dy)
            if cand < best[0]:
                best = (cand, score)

    return [best[0][0], best[0][1]]
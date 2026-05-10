def choose_move(observation):
    w = int(observation.get("grid_width", 8)); h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    uncla = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = [0, 0]; bestv = -10**18
    oppx, oppy = observation.get("opponent_position", [w - 1, h - 1])

    def dman(x1, y1, x2, y2): 
        return abs(x1 - x2) + abs(y1 - y2)

    # Build a few local target points: unclaimed near our territory, and opponent territory near ours
    frontier_uncla = []
    for (x, y) in uncla:
        if dman(x, y, sx, sy) <= 5:
            for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
                nx, ny = x + dx, y + dy
                if (nx, ny) in selfT:
                    frontier_uncla.append((x, y))
                    break
    frontier_uncla = frontier_uncla[:6]

    opp_near = []
    for (x, y) in oppT:
        if dman(x, y, sx, sy) <= 6:
            # prefer opponent cells that are close to our territory
            for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
                nx, ny = x + dx, y + dy
                if (nx, ny) in selfT:
                    opp_near.append((x, y))
                    break
    opp_near = opp_near[:6]

    # Evaluation
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        v = 0
        if (nx, ny) in oppT:
            v += 260  # flipping swing
            v += 30 - dman(nx, ny, oppx, oppy) * 2  # disrupt opponent advance
        elif (nx, ny) in uncla:
            v += 80  # claim growth
        elif (nx, ny) in selfT:
            v += 10

        # Move toward best frontier/unclaimed to keep territory expanding
        if frontier_uncla:
            v += 40 - min(dman(nx, ny, tx, ty) for (tx, ty) in frontier_uncla) * 3
        if opp_near:
            # If we can reach opponent near our border, prefer it
            v += 25 - min(dman(nx, ny, ox, oy) for (ox, oy) in opp_near) * 2

        # Keep away from being trapped by opponent: avoid stepping closer if opponent is near
        opp_dist = dman(nx, ny, oppx, oppy)
        v -= max(0, 4 - opp_dist) * 8

        # Small tie-breaker: prefer not to waste moves when equal
        v -= (0 if (dx, dy) == (0, 0) else 0)

        if v > bestv or (v == bestv and (dx, dy) == (0, 0) and best != [0, 0]):
            bestv = v; best = [dx, dy]

    return best
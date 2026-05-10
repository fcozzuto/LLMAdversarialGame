def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def neigh_counts(x, y):
        c_un = 0
        c_opp = 0
        c_self = 0
        for dx, dy in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h:
                if (nx, ny) in oppT:
                    c_opp += 1
                elif (nx, ny) in unclaimed:
                    c_un += 1
                elif (nx, ny) in selfT:
                    c_self += 1
        return c_un, c_opp, c_self

    best = None
    bestv = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        c_un, c_opp, c_self = neigh_counts(nx, ny)

        # Immediate gain shaping:
        cell = 0
        if (nx, ny) in oppT:
            cell += 30  # flipping opponent cell
        elif (nx, ny) in unclaimed:
            cell += 18
        elif (nx, ny) in selfT:
            cell += 2

        # Contest: move toward opponent to cut off sweeper
        dist = abs(nx - ox) + abs(ny - oy)
        approach = -dist

        # Avoid being passive: reward adjacency to opponent for capture opportunities
        pressure = 6 * c_opp + 2 * c_un - 1 * c_self

        v = cell + approach + pressure

        if bestv is None or v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]
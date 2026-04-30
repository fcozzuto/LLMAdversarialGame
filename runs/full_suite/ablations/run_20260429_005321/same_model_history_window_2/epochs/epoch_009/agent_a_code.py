def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 1)
    h = observation.get("grid_height", 1)

    res = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obstacles_list:
        obstacles.add((p[0], p[1]))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy))

    if not valid:
        return [0, 0]

    if res:
        # Greedy toward nearest resource; tie-break by deterministic ordering in moves list.
        best = None
        bestd = 10**18
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            mind = 10**18
            for r in res:
                rx, ry = r[0], r[1]
                d = abs(nx - rx) + abs(ny - ry)
                if d < mind:
                    mind = d
                    if mind == 0:
                        break
            if mind < bestd:
                bestd = mind
                best = (dx, dy)
        return [best[0], best[1]]

    # No resources: deter opponent by moving to maximize Chebyshev distance.
    best = None
    bestv = -10**18
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        d = max(abs(nx - ox), abs(ny - oy))
        if d > bestv:
            bestv = d
            best = (dx, dy)
    return [best[0], best[1]]
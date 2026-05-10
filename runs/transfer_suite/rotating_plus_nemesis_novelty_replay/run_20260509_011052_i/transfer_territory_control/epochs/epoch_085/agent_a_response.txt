def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    oxp, oyp = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, oxp, oyp = int(sx), int(sy), int(oxp), int(oyp)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_terr = set()
    for p in (observation.get("self_territory", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            self_terr.add((int(p[0]), int(p[1])))

    opp_terr = set()
    for p in (observation.get("opponent_territory", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp_terr.add((int(p[0]), int(p[1])))

    unclaimed = set()
    for p in (observation.get("unclaimed_cells", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.add((int(p[0]), int(p[1])))

    if opp_terr:
        ax = sum(x for x, y in opp_terr) / len(opp_terr)
        ay = sum(y for x, y in opp_terr) / len(opp_terr)
    else:
        ax, ay = float(oxp), float(oyp)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        dist_cent = abs(nx - ax) + abs(ny - ay)
        if (nx, ny) in opp_terr:
            val = 120 - dist_cent  # strong push into opponent control (flipping on entry)
        elif (nx, ny) in unclaimed:
            val = 45 - dist_cent  # expand into unknown
        elif (nx, ny) in self_terr:
            val = 18 - dist_cent  # keep compact
        else:
            val = 5 - dist_cent   # neutral step

        # small tie-breaker: favor progress toward opponent centroid
        val += -0.01 * (abs(nx - ax) + abs(ny - ay))

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move
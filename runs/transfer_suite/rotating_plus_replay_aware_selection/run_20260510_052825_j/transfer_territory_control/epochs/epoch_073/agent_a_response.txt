def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    x, y = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [7, 7])
    ox, oy = op[0], op[1]

    def toset(lst):
        s = set()
        for p in lst or []:
            if p is not None and len(p) >= 2:
                s.add((p[0], p[1]))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    selfT = toset(observation.get("self_territory"))
    oppT = toset(observation.get("opponent_territory"))

    if not observation.get("turn_index", 0) and not unclaimed and not oppT:
        return [0, 0]
    if not unclaimed and not oppT:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]
    deltas.sort()

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def adj_unclaimed(nx, ny):
        c = 0
        for ddx, ddy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]:
            ax, ay = nx + ddx, ny + ddy
            if inb(ax, ay) and (ax, ay) in unclaimed:
                c += 1
        return c

    best = None
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0
        if (nx, ny) in unclaimed:
            score += 20
        elif (nx, ny) in oppT:
            score += 8
        elif (nx, ny) in selfT:
            score += 2
        else:
            score += 0

        score += 2 * adj_unclaimed(nx, ny)

        # Pressure: move closer to opponent when it helps expansion/flip.
        md = abs(nx - ox) + abs(ny - oy)
        score += (6 if ((nx, ny) in unclaimed or (nx, ny) in oppT) else 1) * (-md)

        # Small preference to avoid getting boxed by obstacles.
        neigh_blocked = 0
        for ddx, ddy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ax, ay = nx + ddx, ny + ddy
            if not inb(ax, ay) or (ax, ay) in obstacles:
                neigh_blocked += 1
        score -= neigh_blocked

        if score > best_score:
            best_score = score
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best
def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    x, y = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    self_terr = set(map(tuple, observation.get("self_territory", [])))
    opp_terr = set(map(tuple, observation.get("opponent_territory", [])))

    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # quick obstacle proximity for safety
    def obstacle_near(nx, ny):
        k = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                ax, ay = nx + ddx, ny + ddy
                if inb(ax, ay) and (ax, ay) in obstacles:
                    k += 1
        return k

    # approximate "front pressure": prefer moves that are adjacent to many unclaimed cells
    def unclaimed_adj(nx, ny):
        c = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                ax, ay = nx + ddx, ny + ddy
                if inb(ax, ay) and (ax, ay) in unclaimed:
                    c += 1
        return c

    def manhattan(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # core heuristics: expand unclaimed, take a good cut on opponent, otherwise keep advancing
        score = 0.0
        if (nx, ny) in unclaimed:
            score += 6.0
        elif (nx, ny) in opp_terr:
            score += 3.0
        elif (nx, ny) in self_terr:
            score += 1.0

        # center control bias
        dc = (abs(nx - cx) + abs(ny - cy))
        score += (4.0 - dc * 0.6)

        # avoid getting stuck near obstacles; also prefer routes with open surroundings
        score += (obstacle_near(nx, ny) * -0.8)

        # prefer expansion to open fronts
        score += unclaimed_adj(nx, ny) * 0.35

        # contest: sometimes prioritize approaching opponent if it likely enables flipping next
        score += (-0.12 * manhattan(nx, ny, ox, oy))
        if (nx, ny) in opp_terr:
            score += 1.5  # entering opponent claims can be decisive

        # deterministic tie-break: smallest (dx,dy) in iteration order already deterministic
        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best
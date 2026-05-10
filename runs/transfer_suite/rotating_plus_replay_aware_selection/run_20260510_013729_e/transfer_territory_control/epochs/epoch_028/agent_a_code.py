def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    x, y = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    obstacles = set(map(tuple, observation.get("obstacles", [])))
    self_ter = set(map(tuple, observation.get("self_territory", [])))
    opp_ter = set(map(tuple, observation.get("opponent_territory", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def adj_count(nx, ny, cellset):
        c = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if inb(tx, ty) and (tx, ty) in cellset:
                    c += 1
        return c

    # Precompute nearest unclaimed "gravity" point without full search
    g = None
    bestd = 10**9
    for ux, uy in unclaimed:
        d = (ux - x) * (ux - x) + (uy - y) * (uy - y)
        if d < bestd:
            bestd, g = d, (ux, uy)
    gx, gy = g if g is not None else (x, y)

    # Prefer edge advancement for this opponent archetype
    edge_bias = 0
    if observation.get("turn_index", 0) % 2 == 0:
        edge_bias = 0.25

    best = [0, 0]
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        adj_self = adj_count(nx, ny, self_ter)
        adj_opp = adj_count(nx, ny, opp_ter)

        base = 0
        if (nx, ny) in self_ter:
            base += 0.6
        elif (nx, ny) in unclaimed:
            base += 3.2
        elif (nx, ny) in opp_ter:
            base += 2.6  # flipping on entry enabled

        # Spread while discouraging getting boxed in by opponent
        score = base + 0.9 * adj_self - 1.6 * adj_opp

        # Move toward nearest unclaimed gravity, but also avoid drifting too close to opponent
        d_to_g = abs(nx - gx) + abs(ny - gy)
        d_to_opp = abs(nx - ox) + abs(ny - oy)
        score += 0.65 * (-(d_to_g)) + 0.15 * (d_to_opp)

        # Edge/corner pressure
        if nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1:
            score += 1.1 + edge_bias

        # Deterministic tie-breaker: prefer moves that reduce distance to gravity, then lexicographic
        if score > best_score or (score == best_score and (abs(nx - gx) + abs(ny - gy), dx, dy) < (abs(best[0] - gx) + abs(best[1] - gy), best[0], best[1])):
            best_score = score
            best = [dx, dy]

    return best
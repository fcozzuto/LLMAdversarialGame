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

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    neigh_unclaimed = 0
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if inb(nx, ny) and (nx, ny) in unclaimed:
            neigh_unclaimed = 1
            break

    nearest_opp = None
    if oppT:
        for ox, oy in oppT:
            d = abs(ox - x) + abs(oy - y)
            if nearest_opp is None or d < nearest_opp[0]:
                nearest_opp = (d, (ox, oy))
    nearest_un = None
    if unclaimed:
        for ux, uy in unclaimed:
            d = abs(ux - x) + abs(uy - y)
            if nearest_un is None or d < nearest_un[0]:
                nearest_un = (d, (ux, uy))

    best_move = (0, 0)
    best = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue

        score = 0.0
        if (nx, ny) in oppT:
            score += 28.0
        if (nx, ny) in unclaimed:
            score += 10.0
        if (nx, ny) in selfT:
            score -= 1.2

        # Frontier pressure: favor reducing distance to nearest target
        if nearest_opp is not None:
            score += 2.5 * (nearest_opp[0] - (abs(nx - nearest_opp[1][0]) + abs(ny - nearest_opp[1][1])))
        if nearest_un is not None:
            score += 1.2 * (nearest_un[0] - (abs(nx - nearest_un[1][0]) + abs(ny - nearest_un[1][1])))

        # Avoid being boxed in by obstacles: penalize moves with many blocked neighbors
        blocked = 0
        for ax, ay in dirs:
            tx, ty = nx + ax, ny + ay
            if not inb(tx, ty):
                blocked += 1
        score -= 0.08 * blocked

        # Small bias to progress toward opponent corner (deterministic)
        ox, oy = observation.get("opponent_position", [w - 1, h - 1])
        score += 0.02 * (manh((x, y), (ox, oy)) - manh((nx, ny), (ox, oy)))

        if score > best:
            best = score
            best_move = (dx, dy)

        # If we can immediately flip opponent territory, prioritize it hard
        if (nx, ny) in oppT:
            if score >= best:
                best_move = (dx, dy)

    # If surrounded and no improvement target nearby, try to stay (valid deterministic fallback)
    return [int(best_move[0]), int(best_move[1])]
def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Opponent centroid for deterministic pressure
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
            nx, ny = px + ddx, py + ddy
            if inb(nx, ny) and (nx, ny) in unclaimed:
                c += 1
        return c

    best_dx, best_dy = 0, 0
    best_score = -10**18
    start_dist = abs(x - ocx) + abs(y - ocy)

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            nx, ny = x, y
            dx, dy = 0, 0

        target = (nx, ny)
        uncl_gain = count_unclaimed_neighbors(nx, ny)

        # Prefer taking unclaimed; strongly punish not advancing toward enemy pressure.
        if target in unclaimed:
            base = 20
        elif target in oppT:
            base = 35  # flipping on entry: convert enemy territory
        elif target in selfT:
            base = 3
        else:
            base = 8  # boundary/unknown (often still valuable)

        dist = abs(nx - ocx) + abs(ny - ocy)
        approach = start_dist - dist  # positive if closer
        score = base + 7 * uncl_gain + 4 * approach

        # Small tie-break toward diagonal/forward expansion to avoid dithering
        if score > best_score or (score == best_score and (dx, dy) < (best_dx, best_dy)):
            best_score = score
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]
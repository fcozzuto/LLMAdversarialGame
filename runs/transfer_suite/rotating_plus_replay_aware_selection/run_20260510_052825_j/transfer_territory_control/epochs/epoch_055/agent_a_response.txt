def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    unclaimed = [(p[0], p[1]) for p in (observation.get("unclaimed_cells") or [])]
    selfT = set((p[0], p[1]) for p in (observation.get("self_territory") or []))
    oppT = set((p[0], p[1]) for p in (observation.get("opponent_territory") or []))

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # If we can flip an opponent cell immediately, do it.
    best_flip = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obstacles and (nx, ny) in oppT:
                d_to_opp = md((nx, ny), (ox, oy))
                score = 1000 - d_to_opp
                if best_flip is None or score > best_flip[0]:
                    best_flip = (score, dx, dy)
    if best_flip is not None:
        return [best_flip[1], best_flip[2]]

    if not unclaimed:
        # Fallback: head toward opponent to counterclaim, else stay.
        tx, ty = ox, oy
    else:
        # Choose a deterministic target among top candidates.
        unclaimed_sorted = sorted(unclaimed)
        best_t = None
        best_s = -10**18
        for tx, ty in unclaimed_sorted[:32]:
            # Prefer cells that are "away" from opponent (reduce their contesting),
            # but not too far from us.
            s = (md((tx, ty), (ox, oy)) - md((tx, ty), (x, y)))
            # Slight bias toward expanding from our corner-ish direction.
            s += 0.01 * (tx + ty) if (x == 0 and y == 0) else 0
            if s > best_s:
                best_s = s
                best_t = (tx, ty)
        tx, ty = best_t

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = x + dx, y + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            moves.append((dx, dy, nx, ny))

    # Evaluate each move by its immediate capture potential and distance progress.
    best = None
    for dx, dy, nx, ny in moves:
        immediate = 0
        if (nx, ny) in oppT:
            immediate += 800
        elif (nx, ny) in unclaimed:
            immediate += 120
        elif (nx, ny) in selfT:
            immediate -= 5
        else:
            immediate += 0

        progress = md((nx, ny), (tx, ty)) - md((x, y), (tx, ty))
        # Prefer moves that reduce distance; penalize increases.
        score = immediate - 40 * progress

        # Avoid stepping into opponent vicinity (helps vs territory_counterclaim).
        score -= 0.5 * md((nx, ny), (ox, oy))

        if best is None or score > best[0]:
            best = (score, dx, dy)

    if best is None:
        return [0, 0]
    return [best[1], best[2]]
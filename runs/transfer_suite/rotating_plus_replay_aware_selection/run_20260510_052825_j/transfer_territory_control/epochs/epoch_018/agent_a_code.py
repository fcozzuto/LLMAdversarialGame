def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    opp_pos = observation["opponent_position"]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Pick a deterministic target: nearest unclaimed, tie by lowest (x,y)
    target = None
    if unclaimed:
        target = min(unclaimed, key=lambda c: (abs(c[0] - x) + abs(c[1] - y), c[0], c[1]))

    best = -10**18
    best_move = (0, 0)
    oxp, oyp = opp_pos
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            nx, ny = x, y  # engine keeps in place on invalid move
        cell = (nx, ny)

        score = 0.0
        if cell in unclaimed:
            score += 4.0
        if cell in oppT:
            score += 3.5  # flipping on entry enabled
        if cell in selfT:
            score += 0.4

        if target is not None:
            score += 1.2 * (- (abs(nx - target[0]) + abs(ny - target[1])))

        # Pressure: if opponent is close, prefer moves that get closer to stealing opportunities
        d_opp = abs(nx - oxp) + abs(ny - oyp)
        d_cur = abs(x - oxp) + abs(y - oyp)
        if d_opp <= 2:
            score += 2.5 * (d_cur - d_opp)  # increase if we move closer
        elif d_opp <= 4:
            score += 0.6 * (d_cur - d_opp)

        # Slight preference for expanding outward (away from own territory center-ish)
        if selfT:
            cx = sum(p[0] for p in selfT) / max(1, len(selfT))
            cy = sum(p[1] for p in selfT) / max(1, len(selfT))
            score += 0.08 * (abs(nx - cx) + abs(ny - cy))

        if score > best or (score == best and (dx, dy) < best_move):
            best = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
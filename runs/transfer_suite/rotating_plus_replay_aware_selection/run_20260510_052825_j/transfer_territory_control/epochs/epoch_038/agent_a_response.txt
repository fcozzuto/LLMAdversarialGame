def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(nx, ny): return 0 <= nx < w and 0 <= ny < h
    def neighbors4(cx, cy):
        return [(cx-1, cy), (cx+1, cy), (cx, cy-1), (cx, cy+1)]
    def man(ax, ay, bx, by):
        d1 = ax - bx
        if d1 < 0: d1 = -d1
        d2 = ay - by
        if d2 < 0: d2 = -d2
        return d1 + d2

    # Pick a target: unclaimed frontier adjacent to opponent territory
    frontier = []
    for ux, uy in unclaimed:
        for tx, ty in neighbors4(ux, uy):
            if (tx, ty) in oppT:
                frontier.append((ux, uy))
                break
    if frontier:
        # deterministic: closest to our position, tie by (x,y)
        tx, ty = min(frontier, key=lambda c: (man(x, y, c[0], c[1]), c[0], c[1]))
    elif unclaimed:
        tx, ty = min(unclaimed, key=lambda c: (man(x, y, c[0], c[1]), c[0], c[1]))
    else:
        # fallback: move toward opponent position
        tx, ty = ox, oy

    best = None
    best_score = -10**9
    # Evaluate local moves including staying
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = x + dx, y + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            score = 0
            if (nx, ny) in oppT:
                score += 8
            elif (nx, ny) in selfT:
                score += 1
            elif (nx, ny) in unclaimed:
                score += 4
            # Prefer closing distance to target
            score += 6 - man(nx, ny, tx, ty)
            # Prefer approaching unclaimed adjacent to opponent (likely flip/claim pressure)
            if (nx, ny) not in obstacles:
                adj_opp_unclaimed = 0
                for a, b in neighbors4(nx, ny):
                    if inb(a, b) and (a, b) in oppT:
                        adj_opp_unclaimed += 1
                score += adj_opp_unclaimed * 1.5
            # Tie-break deterministically: smallest |dx|+|dy| then lexicographic
            tie = (abs(dx) + abs(dy), dx, dy)
            if score > best_score or (score == best_score and tie < best):
                best_score = score
                best = tie
                best_move = [dx, dy]

    # If all moves were invalid (should be rare), stay
    if best is None:
        return [0, 0]
    return best_move
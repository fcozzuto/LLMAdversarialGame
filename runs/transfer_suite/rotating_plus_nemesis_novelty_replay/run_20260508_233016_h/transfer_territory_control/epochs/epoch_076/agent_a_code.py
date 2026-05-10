def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = observation.get("unclaimed_cells") or []

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    # Pick a deterministic "frontier" target: unclaimed adjacent to opponent territory, else adjacent to ours, else closest.
    best = None
    best_key = None
    dirs8 = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
    def adj_to_set(cell, S):
        x, y = cell
        for dx, dy in dirs8:
            nx, ny = x + dx, y + dy
            if (nx, ny) in S:
                return True
        return False

    if unclaimed:
        for c in unclaimed:
            x, y = c
            if not inb(x, y): 
                continue
            aop = adj_to_set((x, y), oppT)
            aue = (x in (0, w-1)) or (y in (0, h-1))
            d_me = man(x, y, sx, sy)
            d_op = man(x, y, ox, oy)
            # prioritize contest with opponent and cutting off, then closeness to us
            key = (0 if aop else 1, 0 if aue else 1, d_op, d_me)
            if best_key is None or key < best_key:
                best_key, best = key, (x, y)

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not candidates:
        return [0, 0]

    # If no target found, steer to opponent with a slight move toward center.
    tx, ty = best if best is not None else (w // 2, h // 2)

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obstacles: 
            continue

        # Immediate cell value
        score = 0
        if (nx, ny) in oppT:
            score += 120 + (8 - man(nx, ny, ox, oy))  # strong flip pressure
        elif (nx, ny) in selfT:
            score += 8  # consolidating
        else:
            # unclaimed or somewhere else
            score += 35 if (nx, ny) not in selfT else 10
            score += 2 if (nx in (0, w-1) or ny in (0, h-1)) else 0

        # Move quality toward target with a "frontier" bias
        d1 = man(nx, ny, tx, ty)
        d0 = man(sx, sy, tx, ty)
        score += (d0 - d1) * 10

        # Tactical block: reduce distance to closest opponent if not flipping now
        score += (man(sx, sy, ox, oy) - man(nx, ny, ox, oy)) * (6 if (nx, ny) not in oppT else 2)

        # Avoid getting too close to opponent only when we're not contesting (prevents passive cornering)
        score -= 3 if (nx, ny) not in oppT and man(nx, ny, ox, oy) <= 1 and (nx, ny) in selfT else 0

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
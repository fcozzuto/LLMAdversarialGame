def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = [tuple(p) for p in (observation.get("unclaimed_cells") or [])]
    unclaimed_set = set(unclaimed)
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Find best next cell among neighbors using target scoring
    def neighbor_score(nx, ny):
        if (nx, ny) in obstacles:
            return -10**9
        base = 0
        if (nx, ny) in oppT:
            base += 1200  # flipping opponent territory on entry
        elif (nx, ny) in unclaimed_set:
            base += 200   # expanding into unclaimed
        elif (nx, ny) in selfT:
            base += 5     # safe hold
        else:
            base += 10    # empty cell still provides progress via neighbor heuristics

        # Encourage approaching promising targets (unclaimed first, then enemy)
        if unclaimed:
            # limited candidate set for determinism and speed
            m = 0
            bestd = 10**9
            bestp = None
            for i in range(min(20, len(unclaimed))):
                c = unclaimed[i]
                d = man(nx, ny, c[0], c[1])
                if d < bestd:
                    bestd = d
                    bestp = c
            if bestp is not None:
                tx, ty = bestp
                base += 35 * max(0, 6 - bestd)
                # prefer reaching enemy edge
                base += 6 * (man(tx, ty, ox, oy) - man(nx, ny, ox, oy)) * 0.1
        # Prefer moving toward opponent if no unclaimed pressure
        base += 2 * (man(sx, sy, ox, oy) - man(nx, ny, ox, oy))

        # Avoid stepping onto positions that are "too deep" inside opponent territory
        if (nx, ny) in oppT:
            base -= 0.5 * man(nx, ny, ox, oy)

        return base

    # If we are surrounded by obstacles/low options, just stay
    best = (0, 0)
    best_sc = neighbor_score(sx, sy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        sc = neighbor_score(nx, ny)
        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    return [int(best[0]), int(best[1])]
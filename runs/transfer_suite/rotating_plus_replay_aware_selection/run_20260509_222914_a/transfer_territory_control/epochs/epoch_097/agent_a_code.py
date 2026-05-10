def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or sp
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_ter = set(tuple(p) for p in (observation.get("self_territory") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    opp_ter = set(tuple(p) for p in (observation.get("opponent_territory") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h

    # Precompute frontier candidates (unclaimed adjacent to our territory)
    frontier = set()
    for (x, y) in self_ter:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0: 
                    continue
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) in unclaimed:
                    frontier.add((nx, ny))

    def move_score(nx, ny):
        if (nx, ny) in obstacles: 
            return -10**9
        s = 0
        if (nx, ny) in frontier:
            s += 120  # strong push into expandable frontier
        if (nx, ny) in unclaimed:
            s += 40
        if (nx, ny) in opp_ter:
            s += 25  # stepping into opponent territory flips on entry
        # Encourage progressing away from opponent while not ignoring frontier
        d_opp = abs(nx - ox) + abs(ny - oy)
        s += d_opp * 0.6
        # Keep some cohesion toward our current territory when no frontier
        if not frontier:
            d_own = 999
            for (ax, ay) in self_ter:
                dd = abs(nx - ax) + abs(ny - ay)
                if dd < d_own: d_own = dd
            s += (20 - d_own) * 2.0
        # Slightly prefer staying within bounds and reducing distance to nearest frontier/unclaimed
        if frontier:
            best = 999
            for (fx, fy) in frontier:
                d = abs(fx - nx) + abs(fy - ny)
                if d < best: best = d
            s += (20 - best) * 1.2
        else:
            if unclaimed:
                best = 999
                for (ux, uy) in unclaimed:
                    d = abs(ux - nx) + abs(uy - ny)
                    if d < best: best = d
                s += (18 - best) * 0.9
        return s

    best_move = (0, 0)
    best_s = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        sc = move_score(nx, ny)
        # Deterministic tie-break: lexicographically smallest (dx,dy) among equal score
        if sc > best_s or (sc == best_s and (dx, dy) < best_move):
            best_s = sc
            best_move = (dx, dy)

    # If all neighbors are blocked, stay
    if best_s == -10**18:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]
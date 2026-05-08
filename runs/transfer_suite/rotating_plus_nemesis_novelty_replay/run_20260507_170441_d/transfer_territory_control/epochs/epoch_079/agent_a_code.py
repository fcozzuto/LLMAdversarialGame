def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    self_t = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_t = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def neigh_counts(x, y):
        un, op, se = 0, 0, 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in unclaimed:
                un += 1
            if (nx, ny) in opp_t:
                op += 1
            if (nx, ny) in self_t:
                se += 1
        return un, op, se

    best = None
    best_sc = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        # If it's an obstacle, engine keeps us in place; penalize this choice.
        hits_obstacle = (nx, ny) in blocked
        un, opn, sen = neigh_counts(nx, ny)

        # Prefer stepping into opponent territory (flipping enabled).
        in_opp = (nx, ny) in opp_t
        dist_now = abs(sx - ox) + abs(sy - oy)
        dist_new = abs(nx - ox) + abs(ny - oy)

        sc = 0
        sc += (6 if in_opp else 0)
        sc += (2 * opn)  # push toward opponent-controlled frontier
        sc += (1 * un)   # expand claim surface
        sc -= (0.3 * sen)  # avoid over-staying inside our dense core
        sc += 0.25 * (dist_now - dist_new)  # small incentive to reduce distance
        sc -= (3 if hits_obstacle else 0)

        if sc > best_sc:
            best_sc = sc
            best = [dx, dy]
        elif sc == best_sc and best is not None:
            # Deterministic tie-break: smallest (dx,dy) in lexicographic order
            if (dx, dy) < (best[0], best[1]):
                best = [dx, dy]

    return [int(best[0]), int(best[1])]
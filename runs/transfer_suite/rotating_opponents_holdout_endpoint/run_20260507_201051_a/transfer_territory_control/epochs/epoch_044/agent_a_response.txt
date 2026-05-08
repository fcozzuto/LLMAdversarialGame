def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sx, sy = observation.get("self_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    resources = set(map(tuple, observation.get("resources") or []))

    adj8 = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    adj4 = [(-1,0),(1,0),(0,-1),(0,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if resources:
        targets = resources
    elif unclaimed:
        targets = unclaimed
    else:
        targets = set()

    best = (0, 0)
    best_sc = -10**18

    # Prefer expanding from our frontier into unclaimed; otherwise chase targets.
    for dx, dy in adj8:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        sc = 0
        if (nx, ny) in unclaimed:
            sc += 200
        if (nx, ny) in opp_t:
            sc += 120  # flipping likely
        if (nx, ny) in self_t:
            sc -= 5

        frontier = False
        if self_t:
            for ddx, ddy in adj4:
                ax, ay = nx + ddx, ny + ddy
                if (ax, ay) in self_t:
                    frontier = True
                    break
        if frontier and (nx, ny) in unclaimed:
            sc += 500
        if frontier and not (nx, ny) in obstacles:
            sc += 30

        if targets:
            # Move toward nearest target (resources/unclaimed), but keep expansion bias above.
            dmin = 10**18
            for tx, ty in targets:
                d = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
                if d < dmin:
                    dmin = d
            sc += -dmin / 10.0

        # Deterministic tie-break: prefer smaller moves vector lexicographically.
        if sc > best_sc or (sc == best_sc and (dx, dy) < best):
            best_sc = sc
            best = (dx, dy)

    return [int(best[0]), int(best[1])]
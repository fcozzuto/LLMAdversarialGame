def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position") or [0, 0])
    ox, oy = map(int, observation.get("opponent_position") or [0, 0])

    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = list(map(tuple, observation.get("unclaimed_cells") or []))
    opp_terr = list(map(tuple, observation.get("opponent_territory") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    cand = []
    nearest_unclaimed = unclaimed[0] if unclaimed else None
    nearest_opp_terr = opp_terr[0] if opp_terr else None

    if unclaimed:
        bestd = 10**9
        for c in unclaimed:
            d = man(sx, sy, c[0], c[1])
            if d < bestd:
                bestd = d
                nearest_unclaimed = c
    else:
        if opp_terr:
            bestd = 10**9
            for c in opp_terr:
                d = man(sx, sy, c[0], c[1])
                if d < bestd:
                    bestd = d
                    nearest_opp_terr = c

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Primary: get to unclaimed quickly (claiming yields immediate territory growth).
        if unclaimed:
            dmin = 10**9
            for ux, uy in unclaimed:
                d = man(nx, ny, ux, uy)
                if d < dmin:
                    dmin = d
            score = -dmin
        else:
            # Secondary: if no unclaimed remain, approach opponent territory to flip on entry.
            dmin = 10**9
            if opp_terr:
                for tx, ty in opp_terr:
                    d = man(nx, ny, tx, ty)
                    if d < dmin:
                        dmin = d
            else:
                dmin = man(nx, ny, w - 1, h - 1)
            score = -dmin

        # Tertiary: prefer being farther from opponent to reduce interruption risk.
        score += 0.08 * man(nx, ny, ox, oy)

        # Deterministic tie-breaker: lexicographic on move.
        cand.append((score, dx, dy))

    if not cand:
        return [0, 0]
    cand.sort(key=lambda t: (-t[0], t[1], t[2]))
    _, dx, dy = cand[0]
    return [int(dx), int(dy)]
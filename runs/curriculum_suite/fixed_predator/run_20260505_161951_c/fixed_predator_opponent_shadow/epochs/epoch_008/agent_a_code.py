def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = [tuple(p) for p in observation.get("resources", [])]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        best = None
        bestv = -10**18
        for dx, dy, nx, ny in moves:
            v = man((nx, ny), (ox, oy))
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Choose a target: maximize (opp_d - self_d), tie-break by smaller self_d
    best_target = None
    best_adv = -10**18
    best_sd = 10**18
    for r in resources:
        sd = man((sx, sy), r)
        od = man((ox, oy), r)
        adv = od - sd
        if adv > best_adv or (adv == best_adv and sd < best_sd):
            best_adv, best_sd, best_target = adv, sd, r

    tx, ty = best_target
    # One-step lookahead scoring for each legal move
    best = None
    bestscore = -10**18
    for dx, dy, nx, ny in moves:
        sd2 = man((nx, ny), (tx, ty))
        od = man((ox, oy), (tx, ty))
        # Primary: improve our competitiveness vs opponent for the target
        score = (od - sd2) * 1000 - sd2
        # Small secondary: avoid stepping adjacent to obstacle-less traps by keeping closer to center-ish of resources
        # (deterministic tie breaker using nearest resource distance)
        if score == bestscore:
            dmin = 10**18
            for r in resources:
                dmin = min(dmin, man((nx, ny), r))
            if dmin < best_sd:
                bestscore = score
                best = (dx, dy)
        elif score > bestscore:
            bestscore = score
            best = (dx, dy)

    return [best[0], best[1]]
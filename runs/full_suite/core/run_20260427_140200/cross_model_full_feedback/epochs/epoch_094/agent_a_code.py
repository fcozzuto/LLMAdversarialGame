def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    mx, my = int(me[0]), int(me[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return not inb(x, y) or (x, y) in obstacles
    def manh(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    mypos = (mx, my)
    opp = (ox, oy)

    if not resources:
        # Retreat or contest opponent if no resources known
        best = (-10**18, 0, 0)
        for dx, dy in moves:
            nx, ny = mx + dx, my + dy
            if blocked(nx, ny): continue
            # Prefer moving away while reducing distance (tie-break)
            sc = (manh(opp, mypos) - manh(opp, (nx, ny))) - 0.01 * manh((nx, ny), opp)
            if sc > best[0]: best = (sc, dx, dy)
        return [best[1], best[2]]

    # Choose resource that we can reach earlier than opponent; otherwise pick best "contested" fallback
    best_move = (-(10**18), 0, 0)
    for dx, dy in moves:
        nx, ny = mx + dx, my + dy
        if blocked(nx, ny): continue
        npos = (nx, ny)

        my_d = manh(npos, opp)
        move_adv = 0.0

        # If we are adjacent to opponent, prioritize separation but still aim for a resource if it helps
        if my_d <= 1:
            move_adv += 6.0 * my_d  # larger is better (away)
        else:
            move_adv += 0.2 * my_d

        # Evaluate best target from this step
        best_target = -(10**18)
        for tx, ty in resources:
            t = (tx, ty)
            d_me = manh(npos, t)
            d_opp = manh(opp, t)

            # Strong preference for winning the race to target; mild distance pressure
            # If opponent is closer, heavily penalize; still allow if penalty can't be avoided.
            race = (d_opp - d_me)
            sc = 10.0 * race - 0.6 * d_me
            # Small bias toward center-ish squares to avoid corner traps
            sc += 0.05 * (3.5 - abs(tx - (w-1)/2)) + 0.05 * (3.5 - abs(ty - (h-1)/2))
            if sc > best_target: best_target = sc

        total = best_target + move_adv
        if total > best_move[0]:
            best_move = (total, dx, dy)

    return [best_move[1], best_move[2]]
def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    obs = set()
    for c in observation.get("obstacles", []) or []:
        if c is not None and len(c) >= 2:
            try:
                obs.add((int(c[0]), int(c[1])))
            except:
                pass

    selfT = observation.get("self_territory") or []
    oppT = observation.get("opponent_territory") or []
    unclaimed = observation.get("unclaimed_cells") or []

    own = set((int(x), int(y)) for x, y in selfT if x is not None and y is not None)
    opp = set((int(x), int(y)) for x, y in oppT if x is not None and y is not None)

    def step_score(nx, ny):
        # Higher is better; deterministic tie-breaking by (score, nx, ny)
        if (nx, ny) in obs:
            return -10**9
        if (nx, ny) in own:
            base = 0
        elif (nx, ny) in opp:
            base = 8  # counterclaim payoff
        else:
            base = 5  # expand into unclaimed/neutral
        # Avoid getting stuck near obstacles
        near_obst = 0
        for dx, dy in dirs:
            x2, y2 = nx + dx, ny + dy
            if inb(x2, y2) and (x2, y2) in obs:
                near_obst += 1
        base -= 1.5 * near_obst
        # Encourage moving toward good targets
        # Prefer nearest unclaimed if available, else nearest opponent cell.
        if unclaimed:
            tx, ty = min(unclaimed, key=lambda t: abs(int(t[0]) - nx) + abs(int(t[1]) - ny))
            dist = abs(tx - nx) + abs(ty - ny)
            base += 3.0 / (1 + dist)
        else:
            if opp:
                tx, ty = min(opp, key=lambda t: abs(t[0] - nx) + abs(t[1] - ny))
                dist = abs(tx - nx) + abs(ty - ny)
                base += 2.5 / (1 + dist)
            else:
                dist = abs(ox - nx) + abs(oy - ny)
                base += 1.5 / (1 + dist)
        return base

    # Choose a neighboring step; if no move improves, stay.
    best = (step_score(sx, sy), sx, sy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sc = step_score(nx, ny)
        cand = (sc, nx, ny)
        if cand > best:
            best = cand
    _, bx, by = best
    return [bx - sx, by - sy]
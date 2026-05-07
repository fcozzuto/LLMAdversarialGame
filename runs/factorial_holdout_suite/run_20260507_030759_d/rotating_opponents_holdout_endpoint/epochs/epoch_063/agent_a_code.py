def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and inb(x, y) and (x, y) not in blocked:
                res.append((x, y))
    if not res:
        return [0, 0]

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    best_cell = None
    best_adv = -10**9
    best_sd = 10**9
    for c in res:
        sd = abs(c[0] - sx) + abs(c[1] - sy)
        od = abs(c[0] - ox) + abs(c[1] - oy)
        adv = od - sd
        if adv > best_adv or (adv == best_adv and sd < best_sd):
            best_adv, best_sd, best_cell = adv, sd, c
    tx, ty = best_cell

    def step_score(nx, ny):
        # Prefer increasing advantage, avoid moving into dead/blocked cells.
        if (nx, ny) in blocked or not inb(nx, ny):
            return (-10**9, 10**9, 10**9)
        # Evaluate best resource from this hypothetical position.
        cur_best = -10**9
        cur_sd = 10**9
        cur_threat = 10**9
        for c in res:
            sd = abs(c[0] - nx) + abs(c[1] - ny)
            od = abs(c[0] - ox) + abs(c[1] - oy)
            adv = od - sd
            # threat: how close opponent is if we are close too (to contest sooner)
            threat = od - sd if od < sd + 3 else od
            if adv > cur_best or (adv == cur_best and sd < cur_sd) or (adv == cur_best and sd == cur_sd and threat < cur_threat):
                cur_best, cur_sd, cur_threat = adv, sd, threat
        # Small tie-break: reduce distance to our chosen target cell.
        target_dist = abs(tx - nx) + abs(ty - ny)
        return (cur_best, -cur_sd, -target_dist)

    # If we're already on a resource, stay to secure collection.
    if (sx, sy) in blocked:
        return [0, 0]
    for c in res:
        if c == (sx, sy):
            return [0, 0]

    best = None
    best_ns = (-10**9, 10**9, 10**9)
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        ns = step_score(nx, ny)
        if best is None or ns > best_ns:
            best_ns = ns
            best_move = [dx, dy]
            best = (nx, ny)

    # If best move doesn't reduce distance to target and we have any other safe improving move, bias toward target.
    curr_td = abs(tx - sx) + abs(ty - sy)
    nx, ny = sx + best_move[0], sy + best_move[1]
    if (abs(tx - nx) + abs(ty - ny)) >= curr_td:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in blocked and (abs(tx - nx) + abs(ty - ny)) < curr_td:
                return [dx, dy]

    return best_move
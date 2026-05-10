def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    self_ter = set()
    for p in observation.get("self_territory", []) or []:
        if p and len(p) >= 2:
            self_ter.add((int(p[0]), int(p[1])))
    opp_ter = set()
    for p in observation.get("opponent_territory", []) or []:
        if p and len(p) >= 2:
            opp_ter.add((int(p[0]), int(p[1])))

    unclaimed = []
    for p in observation.get("unclaimed_cells", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if ok(x, y):
                unclaimed.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if unclaimed:
        best_val = 10**18
        tx, ty = unclaimed[0]
        for x, y in unclaimed:
            du = abs(x - sx) + abs(y - sy)
            do = abs(x - ox) + abs(y - oy)
            val = (du - 0.25 * do) + 0.02 * (x + y)  # tie-break deterministic
            if val < best_val:
                best_val = val
                tx, ty = x, y
    else:
        tx, ty = ox, oy

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        du = abs(tx - nx) + abs(ty - ny)
        do = abs(tx - ox) + abs(ty - oy)  # approximate pressure from opponent side

        s = -du
        if (nx, ny) in opp_ter:
            s += 80
        elif (nx, ny) in self_ter:
            s += 10
        else:
            s += 2  # unclaimed/neutral
        if unclaimed:
            us_first = 1 if (abs(tx - nx) + abs(ty - ny)) <= (abs(tx - ox) + abs(ty - oy)) else 0
            s += 6 * us_first
        s += 0.001 * ((nx - sx) * 7 + (ny - sy) * 13)
        if s > best_score:
            best_score = s
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
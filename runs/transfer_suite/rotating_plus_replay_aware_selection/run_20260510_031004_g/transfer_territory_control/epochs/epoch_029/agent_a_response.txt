def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    px, py = observation.get("opponent_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    self_terr = set(map(tuple, observation.get("self_territory", [])))
    opp_terr = set(map(tuple, observation.get("opponent_territory", [])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if unclaimed:
        tx, ty = min(unclaimed, key=lambda t: (man(sx, sy, t[0], t[1]), man(px, py, t[0], t[1])))
        target = (tx, ty)
    else:
        opp_cells = list(opp_terr)
        if opp_cells:
            tx, ty = min(opp_cells, key=lambda t: (man(sx, sy, t[0], t[1]), man(px, py, t[0], t[1])))
            target = (tx, ty)
        else:
            target = (7 - sx, 7 - sy)

    best = (0, 0)
    best_val = -10**18
    tpx = px + (1 if px < sx else (-1 if px > sx else 0))
    tpy = py + (1 if py < sy else (-1 if py > sy else 0))
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        val = 0
        if (nx, ny) in unclaimed:
            val += 520
        if (nx, ny) in opp_terr:
            val += 240  # flipping on entry is valuable
        if (nx, ny) in self_terr:
            val += 35

        # Drive toward a target (claim/flip frontier), but keep some distance from opponent
        val += -man(nx, ny, target[0], target[1])
        val += 0.35 * (man(sx, sy, tpx, tpy) - man(nx, ny, tpx, tpy))

        # Frontier pressure: being adjacent to opponent territory is good if we aren't just staying idle
        adj_opp = False
        for ax, ay in dirs:
            ex, ey = nx + ax, ny + ay
            if inb(ex, ey) and (ex, ey) in opp_terr:
                adj_opp = True
                break
        if adj_opp:
            val += 75

        # Avoid stepping into opponent-controlled pockets unless we can flip immediately
        if (nx, ny) not in opp_terr and adj_opp:
            val -= 10

        if val > best_val:
            best_val = val
            best = (dx, dy)

    dx, dy = best
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1) or not free(sx + dx, sy + dy):
        return [0, 0]
    return [dx, dy]
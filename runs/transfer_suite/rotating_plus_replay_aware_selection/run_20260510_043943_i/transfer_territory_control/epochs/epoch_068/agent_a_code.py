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

    self_t = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_t = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))

    unclaimed = []
    for x, y in (observation.get("unclaimed_cells") or []):
        x, y = int(x), int(y)
        if ok(x, y):
            unclaimed.append((x, y))

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if unclaimed:
        best_t = None
        best_val = -10**18
        for x, y in unclaimed:
            ds = abs(x - sx) + abs(y - sy)
            do = abs(x - ox) + abs(y - oy)
            v = (do - ds) * 3 - ds
            if v > best_val:
                best_val = v
                best_t = (x, y)
        tx, ty = best_t
    else:
        tx, ty = ox, oy

    best_move = (0, 0)
    best_sc = -10**18
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_to_target = abs(tx - nx) + abs(ty - ny)
        d_to_opp = abs(ox - nx) + abs(oy - ny)
        cell = (nx, ny)

        sc = 0
        if cell in opp_t:
            sc += 20 - d_to_target
        elif cell in self_t:
            sc += 6 - d_to_target
        else:
            sc += 4 - d_to_target

        if cell in set(unclaimed):
            sc += 10

        sc += (d_to_opp * -0.4)  # don't walk into opponent
        # prefer advancing toward target
        if abs(tx - nx) + abs(ty - ny) < abs(tx - sx) + abs(ty - sy):
            sc += 3

        if sc > best_sc:
            best_sc = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
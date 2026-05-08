def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    self_t = set((int(c[0]), int(c[1])) for c in (observation.get("self_territory") or []) if c is not None and len(c) >= 2)
    opp_t = set((int(c[0]), int(c[1])) for c in (observation.get("opponent_territory") or []) if c is not None and len(c) >= 2)
    unclaimed = set((int(c[0]), int(c[1])) for c in (observation.get("unclaimed_cells") or []) if c is not None and len(c) >= 2)

    targets = list(opp_t)
    if not targets:
        targets = list(unclaimed)
    if not targets:
        return [0, 0]

    dirs = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d1 = abs(nx - ox) + abs(ny - oy)
        if (nx, ny) in opp_t:
            cat = 6
        elif (nx, ny) in unclaimed:
            cat = 4
        elif (nx, ny) in self_t:
            cat = 1
        else:
            cat = 0
        # steer to nearest relevant target, with tie-breakers for determinism
        md = 10**9
        for tx, ty in targets:
            if abs(tx - nx) + abs(ty - ny) < md:
                md = abs(tx - nx) + abs(ty - ny)
        val = cat * 100000 - md * 10 - d1
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
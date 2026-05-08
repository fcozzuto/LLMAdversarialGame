def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    self_t = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_t = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    myc = int(observation.get("self_territory_count", len(self_t)) or len(self_t))
    opc = int(observation.get("opponent_territory_count", len(opp_t)) or len(opp_t))
    behind = myc < opc

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    dirs9 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def frontier_bonus(x, y):
        b = 0
        for dx, dy in dirs4:
            nx, ny = x + dx, y + dy
            if (nx, ny) in unclaimed:
                b += 1
        return 120 * b

    best = (None, -10**18)
    for dx, dy in dirs9:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0

        v = 0
        if (nx, ny) in opp_t:
            v += 1500 if behind else 1200
        elif (nx, ny) in unclaimed:
            dpo = abs(nx - ox) + abs(ny - oy)
            v += (700 if behind else 500) + 40 * (8 - dpo)
        elif (nx, ny) in self_t:
            v += 120
        else:
            v -= 60

        v += frontier_bonus(nx, ny)
        v += 30 * (16 - (abs(nx - sx) + abs(ny - sy)))
        v += int(25 - 0.6 * (abs(nx - cx) + abs(ny - cy)))
        if behind:
            v += 18 * (10 - (abs(nx - ox) + abs(ny - oy)))
        else:
            v -= 12 * (abs(nx - ox) + abs(ny - oy))

        if (v, -abs(dx) - abs(dy)) > best[1:]:
            best = ((dx, dy), v)

    dx, dy = best[0] if best[0] is not None else (0, 0)
    return [int(dx), int(dy)]
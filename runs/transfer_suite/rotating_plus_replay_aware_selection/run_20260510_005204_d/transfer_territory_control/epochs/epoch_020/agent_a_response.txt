def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except:
            pass

    self_set = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_set = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = list((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def score_target(tx, ty):
        d_self = abs(tx - sx) + abs(ty - sy)
        d_opp = abs(tx - ox) + abs(ty - oy)
        lead = d_opp - d_self  # positive if we can reach sooner
        to_center = abs(tx - cx) + abs(ty - cy)
        block = 0
        for dx, dy in dirs:
            nx, ny = tx + dx, ty + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                block += 1
        return (lead * 40) - (d_self * 6) + (block * 3) - (to_center * 1)

    if unclaimed:
        best_tx, best_ty = min(unclaimed, key=lambda p: (-score_target(p[0], p[1]), p[0], p[1]))
    else:
        # Fallback: try to press toward opponent, but still keep our center bias
        best_tx, best_ty = ox, oy

    best = (-10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        val = 0
        # capture/flip incentive
        if (nx, ny) in opp_set:
            val += 220
        # avoid stepping into opponent territory too early if it lets them snap back
        d_after_opp = abs(nx - ox) + abs(ny - oy)
        val += (d_after_opp * 2)
        # expand toward chosen target
        val += -((abs(nx - best_tx) + abs(ny - best_ty)) * 8)
        # keep center pressure when targets are scarce
        val += -((abs(nx - cx) + abs(ny - cy)) * 2)
        # slight preference to not move if scores look equivalent (deterministic tie-break)
        if dx == 0 and dy == 0:
            val += 1

        if (val, -dx, -dy) > best:
            best = (val, dx, dy)

    return [int(best[1]), int(best[2])]
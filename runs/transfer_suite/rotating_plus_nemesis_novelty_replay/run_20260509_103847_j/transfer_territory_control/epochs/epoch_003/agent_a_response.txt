def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    unclaimed = observation.get("unclaimed_cells") or []
    myT = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opT = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # If unclaimed exists, target the one that best advances "pressure" near opponent.
    # Otherwise, step toward opponent territory to counterclaim (flipping on entry helps).
    if unclaimed:
        tx, ty = min(unclaimed, key=lambda c: (abs(int(c[0]) - ox) + abs(int(c[1]) - oy), abs(int(c[0]) - sx) + abs(int(c[1]) - sy)))
    else:
        if opT:
            tx, ty = min(opT, key=lambda c: (abs(c[0] - ox) + abs(c[1] - oy), abs(c[0] - sx) + abs(c[1] - sy)))
        else:
            tx, ty = ox, oy

    best = (0, 0)
    bestv = -10**18

    for dx, dy in dirs:
        nx, ny = int(sx) + dx, int(sy) + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # Score move: prefer getting closer to target, avoid my own turf traps,
        # and strongly prefer entering opponent turf (flip).
        d_to_target = abs(nx - int(tx)) + abs(ny - int(ty))
        d_to_opp = abs(nx - int(ox)) + abs(ny - int(oy))
        already_mine = 1 if (nx, ny) in myT else 0
        hits_op = 1 if (nx, ny) in opT else 0
        is_unclaimed = 1 if (nx, ny) in set((int(x), int(y)) for x, y in unclaimed) else 0

        # Heuristic: pushing into opponent territory is high value; otherwise carve unclaimed;
        # penalize staying and moving deep back into my current region.
        v = 0
        v += 60 * hits_op
        v += 8 * is_unclaimed
        v += -2.2 * d_to_target
        v += 0.6 * d_to_opp
        v += -7 * already_mine
        v += -0.5 * (dx == 0 and dy == 0)

        # Tiny tie-breaker: avoid obstacles-adjacent congestion by minimizing immediate blocked neighbors
        blocked = 0
        for x2, y2 in ((nx - 1, ny), (nx + 1, ny), (nx, ny - 1), (nx, ny + 1)):
            if not inb(x2, y2) or (x2, y2) in obs:
                blocked += 1
        v += -0.3 * blocked

        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]
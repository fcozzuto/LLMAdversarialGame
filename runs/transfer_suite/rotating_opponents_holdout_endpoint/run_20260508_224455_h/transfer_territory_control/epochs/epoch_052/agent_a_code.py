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

    own = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []) if x is not None and y is not None)
    opp = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []) if x is not None and y is not None)
    unclaimed = observation.get("unclaimed_cells") or []

    def obst_neigh(x, y):
        cnt = 0
        for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obs:
                cnt += 1
        return cnt

    # Deterministic target: prefer unclaimed cells that reduce distance to opponent while being reachable locally.
    best_target = None
    best_tval = -10**18
    for tx, ty in unclaimed[:64]:
        tx, ty = int(tx), int(ty)
        if (tx, ty) in obs:
            continue
        d_to_opp = abs(tx - ox) + abs(ty - oy)
        d_from_self = abs(tx - sx) + abs(ty - sy)
        tval = (20 - d_to_opp) - 0.25 * d_from_self
        # Slightly bias toward nearer to center to reduce edge-sticking
        tval += -0.05 * (abs(tx - (w - 1) / 2.0) + abs(ty - (h - 1) / 2.0))
        if tval > best_tval:
            best_tval, best_target = tval, (tx, ty)

    if best_target is None:
        best_target = (ox, oy)

    tx, ty = best_target

    def cell_value(nx, ny):
        if (nx, ny) in obs:
            return -10**12
        if (nx, ny) in opp:
            base = 120  # flipping is strong
        elif (nx, ny) in own:
            base = 8  # keep territory
        else:
            base = 35  # claim expansion/neutral
        # Move pressure: get closer to opponent and target
        d_opp = abs(nx - ox) + abs(ny - oy)
        d_t = abs(nx - tx) + abs(ny - ty)
        # Avoid obstacles crowding
        safe = -6 * obst_neigh(nx, ny)
        return base + (80 - 2.0 * d_opp) + (60 - 1.5 * d_t) + safe

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        score = cell_value(nx, ny)
        # deterministic tie-break
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
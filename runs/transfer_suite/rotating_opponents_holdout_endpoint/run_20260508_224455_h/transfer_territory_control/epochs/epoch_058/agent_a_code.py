def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    sx, sy = int(sx), int(sy)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    obs_set = set()
    for c in (observation.get("obstacles") or []):
        if c is not None and len(c) >= 2:
            try:
                obs_set.add((int(c[0]), int(c[1])))
            except:
                pass

    unclaimed = set()
    for c in (observation.get("unclaimed_cells") or []):
        if c is not None and len(c) >= 2:
            try:
                unclaimed.add((int(c[0]), int(c[1])))
            except:
                pass

    self_terr = set()
    for c in (observation.get("self_territory") or []):
        if c is not None and len(c) >= 2:
            try:
                self_terr.add((int(c[0]), int(c[1])))
            except:
                pass

    opp_terr = set()
    for c in (observation.get("opponent_territory") or []):
        if c is not None and len(c) >= 2:
            try:
                opp_terr.add((int(c[0]), int(c[1])))
            except:
                pass

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    my_count = int(observation.get("self_territory_count", len(self_terr)) or 0)
    opp_count = int(observation.get("opponent_territory_count", len(opp_terr)) or 0)
    trailing = opp_count - my_count

    opp_pos = observation.get("opponent_position") or [w - 1, h - 1]
    ox, oy = int(opp_pos[0]), int(opp_pos[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    best = (0, 0)
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue

        # Territory value
        if (nx, ny) in opp_terr:
            v = 8.0
        elif (nx, ny) in unclaimed:
            v = 3.5
        elif (nx, ny) in self_terr:
            v = 1.2
        else:
            v = 1.0

        # Center pressure (good for territory_center_claim)
        dct = abs(nx - cx) + abs(ny - cy)
        v += 2.4 * (8.0 - dct) / 8.0

        # If trailing, push toward opponent; if ahead, prioritize frontier expansion via center
        dot = abs(nx - ox) + abs(ny - oy)
        if trailing > 0:
            v += 1.6 * (20.0 - dot) / 20.0
        else:
            v += 0.3 * (20.0 - dot) / 20.0

        # Mild anti-obstacle / keep options open: count free adjacent cells
        free = 0
        for adx, ady in dirs:
            tx, ty = nx + adx, ny + ady
            if inb(tx, ty) and (tx, ty) not in obs_set:
                free += 1
        v += 0.08 * free

        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]
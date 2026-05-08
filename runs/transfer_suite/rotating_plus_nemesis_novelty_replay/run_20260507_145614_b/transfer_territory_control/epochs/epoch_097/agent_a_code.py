def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obs.add((x, y))

    self_set = set()
    for p in (observation.get("self_territory") or []):
        if p and len(p) >= 2 and inb(int(p[0]), int(p[1])):
            self_set.add((int(p[0]), int(p[1])))

    opp_set = set()
    for p in (observation.get("opponent_territory") or []):
        if p and len(p) >= 2 and inb(int(p[0]), int(p[1])):
            opp_set.add((int(p[0]), int(p[1])))

    unclaimed = []
    for p in (observation.get("unclaimed_cells") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obs and (x, y) not in self_set and (x, y) not in opp_set:
                unclaimed.append((x, y))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    if not unclaimed:
        for x in range(w):
            for y in range(h):
                if (x, y) not in obs and (x, y) not in self_set and (x, y) not in opp_set:
                    unclaimed.append((x, y))
        if not unclaimed:
            return [0, 0]

    best = None
    best_key = None
    ux, uy = observation.get("opponent_position", [None, None])
    oppx = int(ux) if ux is not None else None
    oppy = int(uy) if uy is not None else None

    for dx, dy in dirs:
        nx, ny = int(sx + dx), int(sy + dy)
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        gain = 0
        if (nx, ny) in self_set:
            gain += 0.2
        elif (nx, ny) in opp_set:
            gain += 3.0  # flipping on entry
        else:
            gain += 1.5  # claim unclaimed/empty

        # Frontier pressure: prefer taking cells closer to unclaimed while staying away from center overcommit
        dcenter = abs(nx - cx) + abs(ny - cy)

        # Find nearest unclaimed distance (cheaper than full search)
        d_un = 10**9
        for tx, ty in unclaimed:
            dd = abs(tx - nx) + abs(ty - ny)
            if dd < d_un:
                d_un = dd

        # If opponent location known, slightly prefer moves that reduce its distance to center
        if oppx is not None and oppy is not None:
            dop = abs(oppx - cx) + abs(oppy - cy)
            dop2 = abs(nx - cx) + abs(ny - cy)
            opp_pressure = 0.2 * (-dop2 + dop)
        else:
            opp_pressure = 0.0

        key = (gain + (0.9 / (1 + d_un)) + opp_pressure, -dcenter, -abs(nx - sx) - abs(ny - sy), -dx, -dy)
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)

    return [int(best[0]), int(best[1])] if best is not None else [0, 0]
def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = to_set("obstacles")
    resources = to_set("resources")
    unclaimed = to_set("unclaimed_cells")
    opp_terr = to_set("opponent_territory")
    self_terr = to_set("self_territory")

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    if opp_terr:
        ax = sum(x for x, y in opp_terr) / float(len(opp_terr))
        ay = sum(y for x, y in opp_terr) / float(len(opp_terr))
        ax, ay = float(ax), float(ay)
    else:
        ax, ay = cx, cy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    adj8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best = None
    bestv = -1e18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        v = 0.0
        if (nx, ny) in opp_terr:
            v += 9.0
        elif (nx, ny) in unclaimed:
            v += 4.0
        elif (nx, ny) in self_terr:
            v += 1.2
        else:
            v += 0.6
        if (nx, ny) in resources:
            v += 1.0

        near_opp = False
        for ddx, ddy in adj8:
            tx, ty = nx + ddx, ny + ddy
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) in opp_terr:
                near_opp = True
                break
        if near_opp:
            v += 2.2

        # Prefer moves toward the opponent territory centroid / center.
        # (Opponent archetype tends to center-claim; contest that region.)
        dist_to_oppcent = ((nx - ax) ** 2 + (ny - ay) ** 2) ** 0.5
        dist_to_center = ((nx - cx) ** 2 + (ny - cy) ** 2) ** 0.5
        v += 2.0 / (1.0 + dist_to_oppcent)
        v += 1.0 / (1.0 + dist_to_center)

        # Slightly reduce chance of mirroring into our own crowded area.
        v -= 0.15 * (1 if (nx, ny) in self_terr else 0)

        if v > bestv:
            bestv = v
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best
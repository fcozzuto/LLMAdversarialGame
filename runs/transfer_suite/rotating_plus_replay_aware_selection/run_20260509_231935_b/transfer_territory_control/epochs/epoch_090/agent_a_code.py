def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    unclaimed = observation.get("unclaimed_cells") or []
    un_set = set()
    for p in unclaimed:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            un_set.add((int(p[0]), int(p[1])))

    st = observation.get("self_territory") or []
    ot = observation.get("opponent_territory") or []
    self_set = set((int(p[0]), int(p[1])) for p in st if isinstance(p, (list, tuple)) and len(p) == 2)
    opp_set = set((int(p[0]), int(p[1])) for p in ot if isinstance(p, (list, tuple)) and len(p) == 2)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    dirs = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def d(ax, ay, bx, by):
        ax -= bx
        ay -= by
        if ax < 0: ax = -ax
        if ay < 0: ay = -ay
        return ax + ay

    # Aim for nearest unclaimed; if none, aim for opponent (to contest) then center.
    targets = list(un_set)
    if not targets:
        targets = [(ox, oy)] if (ox, oy) not in obs else [(int(cx), int(cy))]

    def nearest_target_score(x, y):
        # smaller distance => larger score
        best = 10**9
        for tx, ty in targets:
            dist = d(x, y, tx, ty)
            if dist < best:
                best = dist
        return -best

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue

        val = 0
        if (nx, ny) in opp_set:
            val += 1200  # flip threat
        elif (nx, ny) in un_set:
            val += 200   # claim new territory
        elif (nx, ny) in self_set:
            val += 30    # reinforce

        # contest / pressure: approach nearest unclaimed; also avoid giving opponent an easy capture
        val += 8 * nearest_target_score(nx, ny)
        val += -3 * d(nx, ny, ox, oy)

        # mild centering to prevent corner-sink
        val += -2 * (abs(nx - cx) + abs(ny - cy))

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move
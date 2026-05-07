def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []
    if not isinstance(sx, int) or not isinstance(sy, int) or sx < 0 or sy < 0 or sx >= w or sy >= h:
        return [0, 0]

    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                oset.add((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    best_target = None
    best_key = None
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = r[0], r[1]
            if not (isinstance(rx, int) and isinstance(ry, int) and inb(rx, ry) and (rx, ry) not in oset):
                continue
            ds = abs(rx - sx) + abs(ry - sy)
            do = abs(rx - ox) + abs(ry - oy)
            # prioritize resources we can reach sooner; if tied, prioritize farther from opponent (more likely denial)
            key = (do - ds, -ds, -abs(rx - ox) - abs(ry - oy))
            if best_key is None or key > best_key:
                best_key = key
                best_target = (rx, ry)

    if best_target is None:
        # No visible resources: drift to a safer corner away from opponent while avoiding obstacles.
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best_corner = None
        best_c = None
        for cx, cy in corners:
            if (cx, cy) in oset:
                continue
            d = abs(cx - sx) + abs(cy - sy)
            score = (abs(cx - ox) + abs(cy - oy), -d)
            if best_c is None or score > best_c:
                best_c = score
                best_corner = (cx, cy)
        tx, ty = best_corner if best_corner is not None else (sx, sy)
    else:
        tx, ty = best_target

    best_move = (0, 0)
    best_m = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in oset:
            continue
        ds = abs(tx - nx) + abs(ty - ny)
        dso = abs(tx - ox) + abs(ty - oy)
        # small tie-break: keep away from opponent to reduce their ability to deny
        away = abs(nx - ox) + abs(ny - oy)
        # also prefer moves that reduce our distance to the current target while not worsening relative race too much
        race = (dso - ds)
        key = (race, -ds, away)
        if best_m is None or key > best_m:
            best_m = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
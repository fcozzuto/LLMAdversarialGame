def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.append((int(p[0]), int(p[1])))

    opp_terr = []
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp_terr.append((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    # Prefer nearest unclaimed; otherwise try to move toward opponent territory.
    if unclaimed:
        for tx, ty in unclaimed:
            dist = abs(tx - sx) + abs(ty - sy)
            candidates.append((dist, tx, ty, 0))  # 0 means unclaimed
        candidates.sort(key=lambda t: t[0])
        candidates = candidates[:12]
    else:
        for tx, ty in opp_terr:
            dist = abs(tx - sx) + abs(ty - sy)
            candidates.append((dist, tx, ty, 1))
        candidates.sort(key=lambda t: t[0])
        candidates = candidates[:12]

    # Add a few "best flip" targets near opponent territory boundary by sampling closest cells to opponent.
    if opp_terr and len(candidates) < 12:
        opp_sorted = sorted([(abs(tx - ox) + abs(ty - oy), tx, ty) for tx, ty in opp_terr])[:6]
        for d, tx, ty in opp_sorted:
            candidates.append((abs(tx - sx) + abs(ty - sy), tx, ty, 1))

    best = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        # Evaluate the move by the best achievable target among candidates.
        move_best = -10**18
        for _, tx, ty, ttype in candidates:
            d_us = abs(nx - tx) + abs(ny - ty)
            d_op = abs(nx - ox) + abs(ny - oy)
            # If target is opponent territory, higher value because flipping is enabled on entry.
            # Also prefer moves that are relatively faster to the target than opponent is.
            rel = d_op - d_us
            edge_bonus = 0
            if tx in (0, w - 1) or ty in (0, h - 1):
                edge_bonus = 0.35
            val = (-1.4 * d_us) + (1.0 * rel) + edge_bonus + (1.8 if ttype == 1 else 0.55)
            # Slightly prefer moves that reduce our distance to current unclaimed/opponent cluster.
            move_best = val if val > move_best else move_best
        if move_best > best_val:
            best_val = move_best
            best = [dx, dy]

    return best if best is not None else [0, 0]
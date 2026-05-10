def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)
    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    my_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    dirs8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def step_toward(ax, ay, tx, ty):
        dx = 0 if tx == ax else (1 if tx > ax else -1)
        dy = 0 if ty == ay else (1 if ty > ay else -1)
        # small tie-break to prefer horizontal when equal
        if abs(tx - ax) >= abs(ty - ay):
            return [dx, dy]
        return [dx, dy]

    # Determine expansion source: nearest of our territory to current position, else current position
    if my_terr:
        src = min(my_terr, key=lambda t: (abs(t[0] - sx) + abs(t[1] - sy), t[0], t[1]))
    else:
        src = (sx, sy)
    cx, cy = src

    # Look for best frontier cell: unclaimed first, then opponent cells if adjacent to our territory
    best = None  # (score, tx, ty)
    for tx, ty in unclaimed | opp_terr:
        if not inb(tx, ty):
            continue
        adj_to_me = False
        adj_to_opp = False
        for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            nx, ny = tx + dx, ty + dy
            if (nx, ny) in my_terr or (nx, ny) == (sx, sy):
                adj_to_me = True
            if (nx, ny) in opp_terr:
                adj_to_opp = True
        # Prefer capturing unclaimed near us; attack opponent only if it helps front expansion
        if not adj_to_me and (tx, ty) not in opp_terr:
            continue
        dist = abs(tx - cx) + abs(ty - cy)
        base = 120 if (tx, ty) in unclaimed else 70
        attack_bonus = 25 if (tx, ty) in opp_terr and adj_to_me else 0
        opp_pressure = 10 if adj_to_opp else 0
        edge_bonus = 6 if (tx == 0 or ty == 0 or tx == w - 1 or ty == h - 1) else 0
        score = base + attack_bonus + opp_pressure + edge_bonus - dist
        if best is None or score > best[0] or (score == best[0] and (tx, ty) < (best[1], best[2])):
            best = (score, tx, ty)

    # If no frontier found, head toward center while avoiding obstacles
    if best is None:
        tx, ty = (w // 2, h // 2)
        return step_toward(sx, sy, tx, ty)

    _, tx, ty = best
    return step_toward(sx, sy, tx, ty)
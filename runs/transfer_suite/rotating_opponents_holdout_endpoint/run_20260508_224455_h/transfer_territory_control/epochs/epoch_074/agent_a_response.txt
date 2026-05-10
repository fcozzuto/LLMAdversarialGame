def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    obst = set()
    for c in observation.get("obstacles") or []:
        if isinstance(c, (list, tuple)) and len(c) >= 2:
            obst.add((int(c[0]), int(c[1])))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.add((int(p[0]), int(p[1])))

    selfT = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            selfT.add((int(p[0]), int(p[1])))

    oppT = []
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            oppT.append((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    neighbors8 = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    target_list = None
    if unclaimed:
        target_list = list(unclaimed)
    elif oppT:
        target_list = oppT
    else:
        target_list = [((w - 1) // 2, (h - 1) // 2)]

    use_unclaimed = bool(unclaimed)

    def cell_score(nx, ny):
        if (nx, ny) in obst:
            return -10**9
        if (nx, ny) in selfT:
            # Prefer cells that border lots of unclaimed.
            border_uncl = 0
            if unclaimed:
                for dx, dy in neighbors8:
                    ax, ay = nx + dx, ny + dy
                    if inside(ax, ay) and (ax, ay) in unclaimed:
                        border_uncl += 1
            return 20 * border_uncl - 2 * (abs(nx - sx) + abs(ny - sy))
        # If unclaimed exists, prioritize capturing it; else prioritize contesting opponent territory.
        bestd = 10**9
        for tx, ty in target_list:
            d = abs(tx - nx) + abs(ty - ny)
            if d < bestd:
                bestd = d
        if use_unclaimed and (nx, ny) in unclaimed:
            return 1000 - bestd
        if (not use_unclaimed) and (nx, ny) in set(oppT):
            # Attack opponent territory directly if we have no unclaimed info.
            return 250 - bestd
        # Otherwise move generally toward the current target.
        return 120 - 3 * bestd

    best_key = None
    best_move = [0, 0]
    oppTset = set(oppT)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obst:
            continue
        # Deterministic tie-break: higher score, then smaller dx, then smaller dy.
        sc = cell_score(nx, ny) if ((nx, ny) not in oppTset or use_unclaimed or True) else cell_score(nx, ny)
        key = (sc, -dx, -dy, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move
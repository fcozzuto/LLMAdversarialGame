def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    obstacles = set(map(tuple, observation.get("obstacles", []) or []))
    unclaimed = observation.get("unclaimed_cells", []) or []
    self_terr = set(map(tuple, observation.get("self_territory", []) or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    # Prefer edge/outer expansion vs opponent center-claimer.
    best = None
    if unclaimed:
        for tx, ty in unclaimed:
            if not inb(tx, ty) or blocked(tx, ty):
                continue
            dcenter = abs(tx - cx) + abs(ty - cy)
            dself = abs(tx - sx) + abs(ty - sy)
            # Larger dcenter is better; break ties closer to us.
            key = (dcenter, -dself)
            if best is None or key > best[0]:
                best = (key, (tx, ty))
    if best is None:
        # Fallback: attack opponent territory cells that are near our position.
        opp_list = [p for p in opp_terr if inb(p[0], p[1]) and not blocked(p[0], p[1])]
        if opp_list:
            tx, ty = min(opp_list, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
            best_t = (tx, ty)
        else:
            best_t = (sx, sy)
    else:
        best_t = best[1]

    tx, ty = best_t

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or blocked(nx, ny):
                continue
            md = abs(nx - tx) + abs(ny - ty)
            score = -md
            if (nx, ny) in unclaimed:
                score += 3.5
            if (nx, ny) in opp_terr:
                score += 4.0  # flipping on entry is valuable
            if (nx, ny) in self_terr:
                score -= 0.5  # prefer expansion
            # Additional deterrence from walking toward center (opponent claims it).
            score -= 0.15 * (abs(nx - cx) + abs(ny - cy))
            # Deterministic tie-break: prefer lexicographically smaller (dx,dy).
            candidates.append((score, dx, dy))
    if not candidates:
        return [0, 0]

    candidates.sort(key=lambda t: (-t[0], t[1], t[2]))
    _, dx, dy = candidates[0]
    return [int(dx), int(dy)]
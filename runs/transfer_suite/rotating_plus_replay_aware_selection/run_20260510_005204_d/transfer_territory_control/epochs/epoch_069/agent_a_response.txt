def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.add((x, y))

    myT = set((int(x), int(y)) for x, y in observation.get("self_territory") or [])
    enT = set((int(x), int(y)) for x, y in observation.get("opponent_territory") or [])

    dirs = [(0, 0), (-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    candidates = []
    if myT:
        for x, y in myT:
            for dx, dy in dirs[1:]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) in unclaimed:
                    candidates.append((nx, ny))
    if not candidates:
        candidates = list(unclaimed)
    if not candidates:
        return [0, 0]

    # Pick best target by advantage over opponent; tie-break deterministically by coordinates.
    best_target = None
    best_adv = None
    for tx, ty in candidates:
        if (tx, ty) in obstacles:
            continue
        myd = abs(tx - sx) + abs(ty - sy)
        opd = abs(tx - ox) + abs(ty - oy)
        adv = myd - opd  # smaller is better for me; convert to higher score
        score = -adv * 10 - myd
        key = (score, -tx, -ty)
        if best_target is None or key > best_adv:
            best_adv = key
            best_target = (tx, ty)

    tx, ty = best_target
    # Move one step toward target; evaluate legal deltas.
    best_move = (0, 0)
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        myd = abs(tx - nx) + abs(ty - ny)
        opd = abs(tx - ox) + abs(ty - oy)
        # Prefer reducing my distance; slightly prefer moves that also approach opponent (deny sweeps).
        key = (-myd * 10 + (abs(tx - (ox - dx)) + abs(ty - (oy - dy))) * 0 - 0, -nx, -ny)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
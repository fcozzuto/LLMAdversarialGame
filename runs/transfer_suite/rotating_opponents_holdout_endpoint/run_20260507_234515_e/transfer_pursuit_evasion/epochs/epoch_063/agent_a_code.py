def choose_move(observation):
    w = int(observation.get("grid_width", 8)) or 8
    h = int(observation.get("grid_height", 8)) or 8
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            try:
                oset.add((int(p[0]), int(p[1])))
            except:
                pass

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    step_pref = []
    dx_t = 0 if ox == sx else (1 if ox > sx else -1)
    dy_t = 0 if oy == sy else (1 if oy > sy else -1)

    # Candidates: include staying still
    candidates = [(0, 0)]
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny) and (nx, ny) not in oset:
                candidates.append((dx, dy))

    # If toward-step is valid, consider it strongly by ordering
    toward = (dx_t, dy_t)
    if toward != (0, 0):
        nx, ny = sx + dx_t, sy + dy_t
        if inside(nx, ny) and (nx, ny) not in oset and toward in candidates:
            candidates.remove(toward)
            candidates.insert(0, toward)

    best = None
    best_key = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy

        # Prefer closer to opponent; tie-break with alignment to chase vector.
        man = abs(nx - ox) + abs(ny - oy)
        cheb = max(abs(nx - ox), abs(ny - oy))
        align = -((dx - dx_t) ** 2 + (dy - dy_t) ** 2)  # higher is better
        # Deterministic tie-breakers:
        key = (man, cheb, -align, dx == 0 and dy == 0, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]
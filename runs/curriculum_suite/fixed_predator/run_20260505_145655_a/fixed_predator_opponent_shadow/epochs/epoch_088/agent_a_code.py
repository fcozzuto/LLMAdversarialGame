def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def sgn(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        # Keep pressure by mirroring opponent direction deterministically
        return [-sgn(ox - x), -sgn(oy - y)]

    best = None
    best_val = None
    best_oppdist = None
    for r in resources:
        tx, ty = r[0], r[1]
        sd = abs(tx - x) + abs(ty - y)
        od = abs(tx - ox) + abs(ty - oy)
        adv = od - sd  # positive means we are closer
        # Prefer more advantage, then larger opponent distance (safer), then closer to reduce travel
        val = adv * 1000 - sd
        if best_val is None or val > best_val or (val == best_val and od > best_oppdist):
            best = (tx, ty)
            best_val = val
            best_oppdist = od

    tx, ty = best
    dx_t = sgn(tx - x)
    dy_t = sgn(ty - y)

    # Ordered candidate moves: toward target first, then other directions, then stay
    candidates = []
    primary = (dx_t, dy_t)
    candidates.append(primary)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if (dx, dy) != primary and (dx, dy) != (0, 0):
                candidates.append((dx, dy))
    candidates.append((0, 0))

    best_move = (0, 0)
    best_score = None
    for dx, dy in candidates:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        sd = abs(tx - nx) + abs(ty - ny)
        od = abs(tx - ox) + abs(ty - oy)  # opponent unchanged this turn
        adv_next = od - sd
        # Also slightly prefer moves that keep us away from opponent to avoid collisions
        opp_close = - (abs(nx - ox) + abs(ny - oy))
        score = adv_next * 1000 - sd + opp_close * 0.001
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    pursuer = ("pursuer" in self_role) or ("pursue" in self_role)
    if ("pursuer" in opp_role) and not ("pursuer" in self_role) and not ("pursue" in self_role):
        pursuer = False

    obs = set()
    for b in observation.get("obstacles", []) or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            obs.add((int(b[0]), int(b[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    order = {d:i for i, d in enumerate(deltas)}  # deterministic tie-break

    best_move = (0, 0)
    best_score = None

    # Simple obstacle "risk": penalize stepping adjacent to obstacles (encourages corridor running).
    def risk(x, y):
        r = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obs:
                    r += 1
        return r

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        # Pursuer wants small d2; Evader wants large d2. Add risk penalty.
        score = (-(d2) if pursuer else d2) - (0.15 * risk(nx, ny))
        if best_score is None or score > best_score or (score == best_score and order[(dx, dy)] < order[best_move]):
            best_score = score
            best_move = (dx, dy)

    # If all blocked/invalid, stay.
    dx, dy = best_move
    return [int(dx), int(dy)]
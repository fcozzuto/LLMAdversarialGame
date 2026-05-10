def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs_set = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_set

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    is_evader = ((observation.get("self_role", "") or "").lower() == "evader")

    # Prefer moves that change x/y toward (or away from) opponent, while avoiding obstacles.
    best = None
    best_sc = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # If blocked to opponent, staying may be chosen.
        d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)

        # Extra: keep away from "walls" near obstacles for evader, and move around obstacles for pursuer.
        near_obs = 0
        for tx in (nx - 1, nx, nx + 1):
            for ty in (ny - 1, ny, ny + 1):
                if (tx, ty) in obs_set:
                    near_obs += 1
        # Deterministic tie-breakers based on move direction.
        align = (dx * (ox - sx) + dy * (oy - sy))
        sc = d2
        if is_evader:
            sc = sc + 0.7 * near_obs + 0.01 * align
        else:
            sc = -sc + 0.35 * near_obs - 0.01 * align

        # Tie-break: smaller lexicographic move index preference based on fixed ordering.
        if best_sc is None or (sc > best_sc if is_evader else sc > best_sc):
            best_sc, best = sc, (dx, dy)

    # If all moves invalid (shouldn't happen), stay.
    if best is None:
        return [0, 0]
    return [best[0], best[1]]
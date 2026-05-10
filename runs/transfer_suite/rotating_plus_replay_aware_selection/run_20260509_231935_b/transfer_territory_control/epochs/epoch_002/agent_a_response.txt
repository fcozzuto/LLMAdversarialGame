def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    obs_set = {tuple(p) for p in obstacles}

    self_terr = observation.get("self_territory", [])
    opp_terr = observation.get("opponent_territory", [])
    self_set = {tuple(p) for p in self_terr}
    opp_set = {tuple(p) for p in opp_terr}

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    unclaimed = observation.get("unclaimed_cells", [])
    un_set = {tuple(p) for p in unclaimed} if unclaimed else set()

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set

    # If unclaimed list exists, target it; otherwise expand toward center.
    has_un = bool(un_set)
    if has_un:
        # Find nearest unclaimed cell in deterministic manner by scan-order.
        best_cell = None
        best_d = None
        for (x, y) in unclaimed:
            if not ok(x, y):
                continue
            d = abs(x - sx) + abs(y - sy)
            if best_d is None or d < best_d or (d == best_d and (x, y) < best_cell):
                best_d = d
                best_cell = (x, y)
        tx, ty = best_cell if best_cell else (ox, oy)
    else:
        tx, ty = (w // 2, h // 2)

    # Score moves: prefer reducing distance to target, gaining opponent cells, avoiding wasting into own already-controlled.
    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        d_t = abs(nx - tx) + abs(ny - ty)
        enter_opp = (nx, ny) in opp_set
        enter_self = (nx, ny) in self_set
        enter_un = (nx, ny) in un_set if has_un else False

        # Deterministic scoring via key; higher score is better.
        score = 0
        score += -d_t * 10
        if enter_opp:
            score += 120
        if enter_un:
            score += 40
        if enter_self:
            score -= 15

        # Mild preference for pushing toward opponent side when target is unavailable.
        if not has_un:
            score += - (abs(nx - ox) + abs(ny - oy)) * 2

        key = (-score, d_t, nx, ny)  # deterministic tie-breakers
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    return best if best is not None else [0, 0]
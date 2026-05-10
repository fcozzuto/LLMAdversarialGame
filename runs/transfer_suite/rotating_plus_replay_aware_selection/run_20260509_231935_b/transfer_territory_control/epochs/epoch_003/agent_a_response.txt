def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    obstacles = observation.get("obstacles", [])
    obs_set = {tuple(p) for p in obstacles}

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_set

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    self_terr = observation.get("self_territory", [])
    opp_terr = observation.get("opponent_territory", [])
    self_set = {tuple(p) for p in self_terr}
    opp_set = {tuple(p) for p in opp_terr}

    unclaimed = observation.get("unclaimed_cells", []) or []
    un_set = {tuple(p) for p in unclaimed}

    # Prefer nearest unclaimed; otherwise capture near opponent; otherwise drift to center.
    if un_set:
        candidates = [p for p in unclaimed if ok(p[0], p[1])]
        mode = 0
    else:
        candidates = []
        mode = 1

    if not candidates:
        adj = set()
        for (x, y) in opp_set:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    nx, ny = x + dx, y + dy
                    if (nx, ny) not in opp_set and (nx, ny) not in self_set and ok(nx, ny):
                        adj.add((nx, ny))
        candidates = sorted(adj) if adj else []
    if not candidates:
        candidates = [(w // 2, h // 2)]

    best = None
    best_key = None
    for (tx, ty) in candidates:
        if not ok(tx, ty):
            continue
        # Key: closest, then deterministic tie-break, with slight bonus for approaching opponent
        d = abs(tx - sx) + abs(ty - sy)
        near_opp = 0
        if mode == 1:
            # if target is adjacent-ish to opponent territory, prefer more
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if (tx + dx, ty + dy) in opp_set:
                        near_opp = 1
                        break
                if near_opp:
                    break
        key = (d, -near_opp, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best if best is not None else (w // 2, h // 2)

    # Choose move that reduces distance; deterministic tie-break prefers greater x then y.
    best_move = (0, 0)
    best_mkey = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = abs(tx - nx) + abs(ty - ny)
        # Prefer moves that enter opponent-owned cells (flipping enabled) slightly.
        enter_bonus = 1 if (nx, ny) in opp_set else 0
        # Deterministic tie-break: lower d, then higher enter_bonus, then smallest dx, then smallest dy.
        mkey = (d, -enter_bonus, dx, dy)
        if best_mkey is None or mkey < best_mkey:
            best_mkey = mkey
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]
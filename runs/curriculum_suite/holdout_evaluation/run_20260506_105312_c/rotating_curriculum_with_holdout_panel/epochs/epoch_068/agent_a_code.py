def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                d = abs(nx - tx) + abs(ny - ty)
                key = (d, dx, dy)
                if best is None or key < best[0]:
                    best = (key, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    def eval_move(nx, ny):
        # For each resource, compute arrival advantage (opp later => good), then pick best resource.
        best_adv = None
        best_sd = None
        best_od = None
        for r in resources:
            if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                continue
            rx, ry = int(r[0]), int(r[1])
            sd = abs(nx - rx) + abs(ny - ry)
            od = abs(ox - rx) + abs(oy - ry)
            adv = od - sd
            # Prefer higher advantage; tie-break by closer self, then farther opponent.
            key = (adv, -sd, od)
            if best_adv is None or key > best_adv:
                best_adv = key
                best_sd = sd
                best_od = od
        # Final preference: maximize advantage, then minimize self distance to chosen resource.
        return (best_adv[0], -best_adv[1], best_adv[2], best_sd, best_od)

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        key = eval_move(nx, ny)
        move_key = (-key[0], key[1], -key[2], dx, dy)  # convert to minimization style
        if best is None or move_key < best[0]:
            best = (move_key, dx, dy)

    if best:
        return [int(best[1]), int(best[2])]
    return [0, 0]
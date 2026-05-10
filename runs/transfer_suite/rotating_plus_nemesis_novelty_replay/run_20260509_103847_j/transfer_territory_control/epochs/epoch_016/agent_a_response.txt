def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    selfT = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opT = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unT = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))
    if not unT:
        unT = set(selfT)

    un_list = list(unT)
    if un_list:
        un_list.sort(key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), abs(p[0] - ox) + abs(p[1] - oy)))
        un_list = un_list[:20]
    else:
        un_list = []

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = -10**18

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs:
            continue

        # Discourage stepping onto opponent territory (flip hurts).
        penalty = 0
        if (nx, ny) in opT:
            penalty += 50

        # Prefer immediate frontier: move that reduces distance to nearby unclaimed.
        if un_list:
            d_un = min(abs(nx - tx) + abs(ny - ty) for tx, ty in un_list)
        else:
            d_un = 0

        # Avoid being too close to opponent (reduces likelihood they'll sweep our cells next).
        d_op = abs(nx - ox) + abs(ny - oy)
        near_bonus = d_op

        # Mild preference to keep expanding (prefer not to stay inside current territory).
        expand = 0 if (nx, ny) in selfT else 1

        score = -2.5 * d_un + 1.2 * near_bonus + 3.0 * expand - penalty
        # Deterministic tie-break: prefer smaller dx, then dy.
        if score > best_score or (score == best_score and (best is None or (dx, dy) < best)):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]
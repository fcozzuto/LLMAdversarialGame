def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    x, y = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.append((int(p[0]), int(p[1])))

    if not unclaimed:
        for p in observation.get("resources") or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                unclaimed.append((int(p[0]), int(p[1])))

    if not unclaimed:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    targets = unclaimed
    self_t = observation.get("self_territory") or []
    opp_t = observation.get("opponent_territory") or []
    self_set = set((int(p[0]), int(p[1])) for p in self_t if isinstance(p, (list, tuple)) and len(p) >= 2)
    opp_set = set((int(p[0]), int(p[1])) for p in opp_t if isinstance(p, (list, tuple)) and len(p) >= 2)

    best = None
    best_key = None
    # Score: maximize reach-advantage over opponent; then prefer nearer and less "edge-hugging"
    for tx, ty in targets:
        if (tx, ty) in obs:
            continue
        dS = man((x, y), (tx, ty))
        dO = man((ox, oy), (tx, ty))
        edge_bias = min(tx, w - 1 - tx, ty, h - 1 - ty)
        # Prefer taking new space: slight boost for unclaimed, small penalty if it's already ours/they have it
        already_mine = 1 if (tx, ty) in self_set else 0
        in_their = 1 if (tx, ty) in opp_set else 0
        adv = dO - dS
        key = (-adv, dS + 2 * in_their + 5 * already_mine, -edge_bias, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best
    # Choose next step among valid neighbors to minimize distance to target while staying deterministic
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_d = None
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        d = (abs(nx - tx) + abs(ny - ty)) * 10 + (abs(nx - ox) + abs(ny - oy))
        if best_d is None or d < best_d or (d == best_d and (dx, dy) < best_move):
            best_d = d
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
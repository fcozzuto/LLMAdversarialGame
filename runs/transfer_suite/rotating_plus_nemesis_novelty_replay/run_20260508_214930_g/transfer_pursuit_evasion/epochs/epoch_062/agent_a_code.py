def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for b in observation.get("obstacles") or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    is_evader = "evader" in (observation.get("self_role", "") or "").lower()
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    # Deterministic tie-break order: prefer axis moves over staying, then sign by fixed order already in deltas.
    # For evader: strongly prefer increasing distance and steering toward a far corner; also avoid moving toward opponent.
    if is_evader:
        tx = 0 if ox >= (w - 1) / 2 else w - 1
        ty = 0 if oy >= (h - 1) / 2 else h - 1
    else:
        tx = ox
        ty = oy

    best_score = None
    best_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d_op = abs(nx - ox) + abs(ny - oy)
        # local lookahead: where opponent could be next is unknown, so just bias toward having control near obstacles
        wall_bias = 0
        if nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1:
            wall_bias = 0.08  # deterministic small bias; helps wall-run style evasion/pincer positioning
        obs_penalty = 0
        # Penalize moves that are "surrounded" by obstacles to reduce accidental trapping.
        neigh = 0
        for ddx, ddy in deltas:
            xx, yy = nx + ddx, ny + ddy
            if not (0 <= xx < w and 0 <= yy < h) or (xx, yy) in obs:
                neigh += 1
        obs_penalty = 0.02 * neigh

        if is_evader:
            # Maximize distance; additionally move toward chosen corner while keeping away from opponent.
            corner_dist = abs(nx - tx) + abs(ny - ty)
            # Prefer increasing distance and staying in higher corner distance (i.e., keep running).
            score = (d_op * 1.0) + (corner_dist * 0.12) + wall_bias - obs_penalty
            # Strongly discourage staying if it doesn't increase distance.
            if dx == 0 and dy == 0:
                score -= 0.2
        else:
            # Minimize distance to evader, but avoid stepping into obstacle-heavy areas.
            corner_dist = abs(nx - tx) + abs(ny - ty)  # here tx,ty == opponent; equivalent
            score = (-corner_dist * 1.0) + wall_bias - obs_penalty
            if dx == 0 and dy == 0:
                score -= 0.15

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    # Pick best target: prioritize resources we are closer to; otherwise contest.
    # Deterministic tie-break: higher (opp-self), then smaller self distance, then lexicographic cell.
    best = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        key = (-(do - ds), ds, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Evaluate each move: (1) avoid obstacles/out-of-bounds, (2) move closer to target,
    # (3) maximize opponent disadvantage after the move, (4) slight penalty for moving away.
    bestm = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        ns = man(nx, ny, tx, ty)
        os = man(nx, ny, ox, oy)  # indirectly discourages letting opponent approach us while contesting
        ds_now = man(sx, sy, tx, ty)
        # Opponent's distance to target stays constant from our move; we use our resulting advantage.
        do = man(ox, oy, tx, ty)
        adv = do - ns
        # Deterministic preference ordering via tuple.
        key = (-adv, ns, -os, ds_now - ns, dx, dy)
        if bestm is None or key < bestm[0]:
            bestm = (key, [dx, dy])

    return bestm[1] if bestm is not None else [0, 0]
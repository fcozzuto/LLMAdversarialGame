def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obs = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Pick a target we are most advantaged toward (opponent farther, ours closer).
    best = None
    for rx, ry in resources:
        sd = abs(rx - sx) + abs(ry - sy)
        od = abs(rx - ox) + abs(ry - oy)
        adv = od - sd
        key = (adv, -sd, rx, ry)
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    # If our chosen target is immediate and blocked, still try to move toward any resource with best local advantage.
    target_fallback = best[1]

    cur_sd = abs(tx - sx) + abs(ty - sy)
    best_move = None
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        nsd = abs(tx - nx) + abs(ty - ny)
        nod = abs(tx - ox) + abs(ty - oy)  # opponent pos unchanged this turn
        # Prefer reducing our distance, and if tied, increase opponent's distance to the target (they may move later).
        # Also lightly discourage staying if we can improve.
        step_gain = cur_sd - nsd
        key = (
            step_gain,
            nsd,
            -nod,
            dx, dy
        )
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    if best_move is None:
        # Deterministic safe fallback: stay.
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]
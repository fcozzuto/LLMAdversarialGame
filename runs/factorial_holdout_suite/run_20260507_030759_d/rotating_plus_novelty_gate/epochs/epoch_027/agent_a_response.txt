def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]
    if not resources:
        dx = 1 if ox > sx else (-1 if ox < sx else 0)
        dy = 1 if oy > sy else (-1 if oy < sy else 0)
        return [dx, dy]

    res = [tuple(r) for r in resources]
    res_set = set(res)
    res_sorted = sorted(res)  # deterministic tie-break

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_move = (0, 0, 10**9, 10**9)  # (primary, secondary, td_x, td_y), higher is better
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        immediate = 1 if (nx, ny) in res_set else 0
        # Choose best resource for this move, but score by advantage vs opponent
        best_primary = -10**9
        best_td = None
        for tx, ty in res_sorted:
            sd = man(nx, ny, tx, ty)
            od = man(ox, oy, tx, ty)
            # Prefer grabbing sooner and denying opponent; also avoid giving opponent "free" captures
            primary = (od - sd) * 10 - sd
            # If equal, prefer lower resource coordinate deterministically
            if primary > best_primary:
                best_primary = primary
                best_td = (tx, ty)
        td_x, td_y = best_td
        primary = best_primary + immediate * 10000
        secondary = -man(nx, ny, td_x, td_y)
        cand = (primary, secondary, td_x, td_y)
        if cand > best_move:
            best_move = cand

    _, _, tx, ty = best_move
    # Convert target direction into a legal move; since legal might not reach directly, keep chosen move by recomputation
    # Recompute to select exact move with that (tx,ty)
    chosen = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in res_set:
            return [dx, dy]
        sd = man(nx, ny, tx, ty)
        od = man(ox, oy, tx, ty)
        primary = (od - sd) * 10 - sd
        if chosen is None:
            chosen = (primary, dx, dy)
        else:
            if primary > chosen[0] or (primary == chosen[0] and (dx, dy) < (chosen[1], chosen[2])):
                chosen = (primary, dx, dy)
    return [chosen[1], chosen[2]]
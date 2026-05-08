def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    res = [(r[0], r[1]) for r in resources if inb(r[0], r[1]) and (r[0], r[1]) not in obs]
    if not res:
        return [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Predict opponent's current nearest resource; avoid it to create a different race lane.
    opp_sorted = sorted(res, key=lambda p: md(ox, oy, p[0], p[1]))
    contested = set()
    if opp_sorted:
        contested.add(opp_sorted[0])
        if len(opp_sorted) > 1:
            contested.add(opp_sorted[1])

    # Choose among non-contested resources if possible; else fall back.
    candidates = [p for p in res if p not in contested]
    if not candidates:
        candidates = res

    # One-step lookahead: choose move maximizing (opponent lead on target) with a tie-break to reduce our distance.
    best = (0, 0)
    best_val = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        cur_best_for_move = -10**18
        for tx, ty in candidates:
            d_self = md(nx, ny, tx, ty)
            d_op = md(ox, oy, tx, ty)
            # Prefer targets we can reach sooner than opponent; strongly avoid losing lanes.
            lane = (d_op - d_self) * 1000 - d_self
            if lane > cur_best_for_move:
                cur_best_for_move = lane
        if cur_best_for_move > best_val:
            best_val = cur_best_for_move
            best = (dx, dy)

    return [int(best[0]), int(best[1])]
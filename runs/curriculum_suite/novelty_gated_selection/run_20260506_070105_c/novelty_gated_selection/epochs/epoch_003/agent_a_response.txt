def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def in_bounds(x, y, w, h):
        return 0 <= x < w and 0 <= y < h

    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    # Choose a contest target that we can reach sooner; boost resources on opponent's current row
    best = None
    best_key = None
    for r in resources:
        mr = (r[0], r[1])
        my_d = man((sx, sy), mr)
        opp_d = man((ox, oy), mr)
        share_row = 1 if mr[1] == oy else 0
        # primary: how much earlier we can arrive vs opponent
        # secondary: prefer on opponent's row; tertiary: nearer
        key = ((opp_d - my_d) + 0.35 * share_row, -my_d, -mr[0], -mr[1])
        if best_key is None or key > best_key:
            best_key = key
            best = mr

    tx, ty = best
    # Local move selection among valid deltas (simple obstacle + bounds aware)
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                moves.append((0, 0))
            else:
                moves.append((dx, dy))

    def step_ok(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny, w, h):
            return False
        if (nx, ny) in obstacles:
            return False
        return True

    # Heuristic for each move: reduce distance to target and (slightly) increase distance from opponent
    best_m = (0, 0)
    best_m_key = None
    for dx, dy in moves:
        if not step_ok(dx, dy):
            continue
        nx, ny = sx + dx, sy + dy
        my_to_t = abs(nx - tx) + abs(ny - ty)
        opp_to_t = abs(ox - tx) + abs(oy - ty)
        my_to_opp = abs(nx - ox) + abs(ny - oy)
        # Encourage continuing row pressure vs opponent sweep: favor moving onto opponent row if tie
        onto_opp_row = 1 if ny == oy else 0
        # primary: closer to target; secondary: push away from opponent a bit; tertiary: row pressure; final deterministic tie
        key = (-my_to_t, my_to_opp, onto_opp_row, -dx, -dy)
        if best_m_key is None or key > best_m_key:
            best_m_key = key
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]
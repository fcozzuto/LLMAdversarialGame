def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        return max(abs(x1 - x2), abs(y1 - y2))  # Chebyshev

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    free_res = [(rx, ry) for (rx, ry) in resources if (rx, ry) not in obstacles]
    # Deterministic ordering for tie-break
    free_res.sort()

    if not free_res:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy, nx, ny in legal:
            key = (dist(nx, ny, cx, cy), dist(nx, ny, ox, oy), dx, dy)
            if best is None or key < best:
                best = key
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    best_key = None
    best_move = (0, 0)

    # Opponent threat: which resources are within their next move distance
    opp_next_targets = set()
    for rx, ry in free_res:
        if dist(ox, oy, rx, ry) <= 1:
            opp_next_targets.add((rx, ry))

    for dx, dy, nx, ny in legal:
        # Capture immediately
        capture = 1 if (nx, ny) in obstacles else 0
        cap_bonus = 0
        if (nx, ny) in set(free_res):
            cap_bonus = 1000000

        # Score against best resource with competition + defense
        best_local = -10**18
        for rx, ry in free_res:
            ds = dist(nx, ny, rx, ry)
            do = dist(ox, oy, rx, ry)
            # Prefer stealing: being closer (ds < do), and also being close overall
            # Reward if we can reach in strictly fewer steps; penalize if opponent is closer.
            rel = do - ds
            # Defensive: if opponent can take it next turn, strongly prefer blocking/capturing it.
            danger = 1 if (rx, ry) in opp_next_targets else 0
            val = (cap_bonus
                   + (3000 if rel > 0 else 0)
                   + (200 if rel > 1 else 0)
                   + (120 if danger and ds == 1 else 0)
                   + (500 if danger and ds == 0 else 0)
                   - (ds * 40)
                   - (max(do - ds, -10) * 25)
                   - (danger * 80))
            # Tie-break within target choice: smaller ds, then larger do, then coords
            key2 = (-val, ds, -do, rx, ry)
            if best_local == -10**18 or key2 < best_key_local:
                best_key_local = key2
                best_local = val

        # Also slightly prefer moving away from opponent to reduce their options
        away = dist(nx, ny, ox, oy)
        # Global tie-break fixed by ordering of deltas already implicit via score key
        key = (-(best_local), -away, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
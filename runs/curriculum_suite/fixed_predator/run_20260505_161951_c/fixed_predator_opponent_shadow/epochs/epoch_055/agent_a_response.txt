def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def king_dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    if not resources:
        tx, ty = (sx + ox) // 2, (sy + oy) // 2
        best, bestv = (0, 0), None
        for dx, dy, nx, ny in moves:
            d = king_dist((nx, ny), (tx, ty))
            v = (d, king_dist((nx, ny), (ox, oy)))
            if bestv is None or v < bestv:
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    best_move = (0, 0)
    best_val = None
    for dx, dy, nx, ny in moves:
        my_dists = []
        win_count = 0
        best_margin = -10**9
        for rx, ry in resources:
            my_d = king_dist((nx, ny), (rx, ry))
            opp_d = king_dist((ox, oy), (rx, ry))
            # Opponent can move one step this turn; if their distance > 0 they reduce by at most 1.
            opp_eff = 0 if opp_d <= 1 else (opp_d - 1)
            margin = opp_eff - my_d  # positive => I reach first after this move
            if margin > 0:
                win_count += 1
                if margin > best_margin:
                    best_margin = margin
            my_dists.append(my_d)
        # Tie-breakers: smaller best my distance, then safer from opponent (avoid early trap)
        min_my = min(my_dists) if my_dists else 0
        opp_close = king_dist((nx, ny), (ox, oy))
        val = (win_count, best_margin, -min_my, -opp_close, dx, dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]
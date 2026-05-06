def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = [tuple(p) for p in observation.get("resources", [])]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # If no resources, drift to maximize separation from opponent while staying safe.
    if not resources:
        best = None
        bestd = -10**9
        for dx, dy, nx, ny in moves:
            d = abs(nx - ox) + abs(ny - oy)
            if d > bestd:
                bestd = d
                best = (dx, dy)
        return [best[0], best[1]]

    # Pick the best move by evaluating resulting position against all resources:
    # prefer resources where we are closer than opponent (opp_dist - self_dist), and also closeness.
    best = (0, 0)
    best_val = -10**18
    best_tiebreak = 10**18
    for dx, dy, nx, ny in moves:
        val = -10**18
        tieb = 10**18
        for r in resources:
            sd = man((nx, ny), r)
            od = man((ox, oy), r)
            adv = od - sd  # positive means we are closer
            # maximize advantage, then minimize our distance to that resource
            if adv > val or (adv == val and sd < tieb):
                val = adv
                tieb = sd
        # slight preference for moves that reduce our best distance to any resource
        if val > best_val or (val == best_val and tieb < best_tiebreak):
            best_val = val
            best_tiebreak = tieb
            best = (dx, dy)

    return [int(best[0]), int(best[1])]
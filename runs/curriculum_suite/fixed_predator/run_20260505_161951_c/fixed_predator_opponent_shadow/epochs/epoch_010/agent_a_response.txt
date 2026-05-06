def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = [tuple(p) for p in observation.get("resources", [])]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources:
        best = None
        bestd = -10**9
        for dx, dy, nx, ny in legal:
            d = abs(nx - ox) + abs(ny - oy)
            if d > bestd:
                bestd = d
                best = (dx, dy)
        return [best[0], best[1]]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Pick a target resource we can contest: maximize relative lead (opp closer -> less desirable).
    best_r = None
    best_adv = -10**18
    best_sd = 10**18
    for r in resources:
        sd = man((sx, sy), r)
        od = man((ox, oy), r)
        adv = od - sd
        if adv > best_adv or (adv == best_adv and sd < best_sd):
            best_adv = adv
            best_sd = sd
            best_r = r

    r = best_r
    # Greedy step: maximize being ahead at the next position; secondary prefer reducing opponent distance a bit.
    best_move = None
    best_score = -10**18
    for dx, dy, nx, ny in legal:
        sd_next = man((nx, ny), r)
        od = man((ox, oy), r)
        adv_next = od - sd_next
        score = 2 * adv_next - sd_next
        # If tied, move to reduce opponent distance to that resource (intercept pressure).
        score2 = -man((nx, ny), (ox, oy))
        if score > best_score or (score == best_score and score2 > -10**18):
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]
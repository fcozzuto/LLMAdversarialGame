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

    if not resources:
        best = None
        bestd = -10**9
        for dx, dy, nx, ny in moves:
            d = abs(nx - ox) + abs(ny - oy)
            if d > bestd:
                bestd = d
                best = (dx, dy)
        return [best[0], best[1]]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Phase target selection: prefer resources where we are ahead (opp closer than us -> we lag)
    best_target = None
    best_adv = -10**18
    best_self = 10**18
    for r in resources:
        sd = man((sx, sy), r)
        od = man((ox, oy), r)
        adv = od - sd
        if adv > 0:
            if adv > best_adv or (adv == best_adv and sd < best_self):
                best_adv = adv
                best_self = sd
                best_target = r

    # If we are not ahead on any resource, still move toward the best "swing" while reducing opponent pressure.
    if best_target is None:
        cand = None
        cand_score = -10**18
        for r in resources:
            sd = man((sx, sy), r)
            od = man((ox, oy), r)
            # want to reduce our distance, but avoid resources where opponent is far too ahead
            score = (-sd) + (max(0, sd - od) * 0.5) + (-(od - sd) * 0.1)
            if score > cand_score:
                cand_score = score
                cand = r
        best_target = cand

    tx, ty = best_target
    # Evaluate next-step move by how much it improves being closer than opponent to the chosen target,
    # with a fallback bias toward general resource acquisition.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy, nx, ny in moves:
        sd_t = man((nx, ny), (tx, ty))
        od_t = man((ox, oy), (tx, ty))
        adv_t = od_t - sd_t  # bigger -> we become closer than opponent
        # secondary: get closer to best overall resource after this move
        best_adv_next = -10**18
        best_sd_next = 10**18
        for r in resources:
            sd = man((nx, ny), r)
            od = man((ox, oy), r)
            adv = od - sd
            if adv > best_adv_next or (adv == best_adv_next and sd < best_sd_next):
                best_adv_next = adv
                best_sd_next = sd
        # tertiary: if no positive advantage exists, maximize distance from opponent a bit (avoid being "shadowed")
        opp_dist = man((nx, ny), (ox, oy))
        val = (adv_t * 4.0) + (best_adv_next * 1.0) + (-best_sd_next * 0.1) + (opp_dist * 0.01 if best_adv_next <= 0 else opp_dist * 0.005)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]
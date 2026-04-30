def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    blocked = set((p[0], p[1]) for p in obs_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in blocked:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    if not resources:
        # Move toward center while keeping away from opponent corner
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy, nx, ny in moves:
            s = cheb((nx, ny), (tx, ty)) + 0.1 * cheb((nx, ny), (ox, oy))
            if best is None or s < best[0] or (s == best[0] and (dx, dy) < best[1]):
                best = (s, (dx, dy))
        return [best[1][0], best[1][1]]

    # Evaluate each candidate by best resource advantage (self gets closer than opponent)
    best_move = None
    best_val = None
    for dx, dy, nx, ny in moves:
        # Prefer immediate resource pickup (reach in 1 move)
        reach_bonus = 0
        if (nx, ny) in blocked:
            continue
        best_res_adv = -10**9
        best_res_tieb = None
        for rx, ry in resources:
            self_d = cheb((nx, ny), (rx, ry))
            opp_d = cheb((ox, oy), (rx, ry))
            # If opponent could reach the resource very soon, heavily penalize
            adv = (opp_d - self_d)
            # Encourage paths that reduce self distance, and block risky nearby opponent threats
            if self_d == 0:
                adv += 100
            if opp_d <= 1 and self_d > 1:
                adv -= 8
            # Slight preference for nearer resources to reduce hopping
            adv -= 0.02 * self_d
            tieb = (-(adv), self_d, cheb((nx, ny), (rx, ry)), rx, ry)
            if best_res_tieb is None or tieb < best_res_tieb:
                best_res_tieb = tieb
                best_res_adv = adv

        # Also add a small safety term: avoid getting too close to opponent unless it's winning
        safety = -0.03 * cheb((nx, ny), (ox, oy))
        val = best_res_adv + safety
        key = (val, -cheb((nx, ny), (ox, oy)), dx, dy)
        if best_val is None or key > best_val:
            best_val = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]
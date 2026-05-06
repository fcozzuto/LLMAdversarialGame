def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

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

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        best = None
        bestv = -10**18
        for dx, dy, nx, ny in moves:
            v = -man(nx, ny, ox, oy)  # keep contact when no resources to steer toward
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # 1-step lookahead with "switcher" flavor: prefer moves that create a clear resource advantage
    # and also keep a modest ability to contest the opponent.
    best = None
    bestv = -10**18
    opp_d_now = man(sx, sy, ox, oy)
    for dx, dy, nx, ny in moves:
        self_d_opp = man(nx, ny, ox, oy)
        advs = []
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            advs.append(od - sd)  # positive => we are closer than opponent (on this move)
        advs.sort(reverse=True)
        best_adv = advs[0]
        second_adv = advs[1] if len(advs) > 1 else -10**9
        # Encourage decisive lead (best_adv) and slight diversity (second_adv) to avoid getting lured.
        # Also slightly penalize moving away from opponent (intercept-lite).
        v = 6 * best_adv + 1.5 * second_adv - 0.25 * self_d_opp + 0.08 * (opp_d_now - self_d_opp)
        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]
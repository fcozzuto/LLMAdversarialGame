def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def man(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0:
            ax = -ax
        ay = y1 - y2
        if ay < 0:
            ay = -ay
        return ax + ay

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
        best = None
        best_key = None
        for dx, dy, nx, ny in moves:
            dmid = man(nx, ny, tx, ty)
            dob = man(nx, ny, ox, oy)
            key = (dmid, -dob, dx == 0 and dy == 0)
            if best_key is None or key < best_key:
                best_key = key
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    # If opponent is close, prioritize denial by moving to the best contested resource
    close_opp = man(sx, sy, ox, oy) <= 2

    best_move = (0, 0)
    best_key = None
    for dx, dy, nx, ny in moves:
        # Pick the single resource that yields max advantage from this move
        best_adv = None
        best_sd = None
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd  # positive means we are closer than opponent to that resource
            if best_adv is None or (adv > best_adv) or (adv == best_adv and sd < best_sd):
                best_adv = adv
                best_sd = sd

        # Secondary objectives:
        # - prefer closer to opponent if we're contesting (shadow denial)
        # - otherwise prefer moving away from opponent slightly while improving resource advantage
        dob = man(nx, ny, ox, oy)
        self_opp_term = -dob if close_opp else dob
        # Penalize staying still
        stay_pen = 1 if (dx == 0 and dy == 0) else 0
        key = (-best_adv, best_sd, self_opp_term, stay_pen)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
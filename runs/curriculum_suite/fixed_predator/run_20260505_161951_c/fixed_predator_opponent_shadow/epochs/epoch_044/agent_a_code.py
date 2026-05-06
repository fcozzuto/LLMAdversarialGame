def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # valid moves (include staying)
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) != (sx, sy) and (nx, ny) in obstacles:
                continue
            moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    # No resources left: contest center/line
    if not resources:
        tx, ty = (sx + ox) // 2, (sy + oy) // 2
        best = None
        for dx, dy, nx, ny in moves:
            d_mid = man(nx, ny, tx, ty)
            d_opp = man(nx, ny, ox, oy)
            # if tied, prefer reducing opponent distance slightly
            key = (d_mid, d_opp)
            if best is None or key < best:
                best = key
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # Choose move that maximizes "who can reach a resource first" advantage.
    best_key = None
    best_move = (0, 0)
    for dx, dy, nx, ny in moves:
        # Pick the single resource with highest advantage from this candidate position
        best_adv = -10**9
        best_self_d = 10**9
        for rx, ry in resources:
            self_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            adv = opp_d - self_d
            if adv > best_adv or (adv == best_adv and self_d < best_self_d):
                best_adv = adv
                best_self_d = self_d

        # If we're behind (adv<0), also try to move to reduce distance to opponent to enable interception.
        d_opp = man(nx, ny, ox, oy)
        # Secondary pressure: closer to the best resource.
        # Deterministic tie-break: prefer smaller dx, then smaller dy after other keys.
        tie = (abs(dx), abs(dy), dx, dy)
        if best_adv >= 0:
            key = (-best_adv, best_self_d, -d_opp, tie)
        else:
            key = (-best_adv, best_self_d, d_opp, tie)

        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]
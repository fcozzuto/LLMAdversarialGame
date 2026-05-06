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

    valid = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                valid.append((dx, dy))
    if not valid:
        return [0, 0]

    ti = observation.get("turn_index", 0)
    parity = (ti & 1) - 0.5

    if not resources:
        tx, ty = (gw - 1) // 2, (gh - 1) // 2
        best = None
        bestv = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            self_mid = man(nx, ny, tx, ty)
            opp_mid = man(ox, oy, tx, ty)
            opp_here = man(nx, ny, ox, oy)
            v = (opp_here - self_mid, -(self_mid + 0.1 * opp_mid), parity)
            if bestv is None or v > bestv:
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    # Choose move that maximizes achievable "possession advantage" over opponent for some resource,
    # while also slightly preferring moves that don't get too close to the opponent.
    best_move = (0, 0)
    best_val = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        opp_here = man(nx, ny, ox, oy)
        best_adv = None
        best_self_d = None
        for rx, ry in resources:
            self_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            # Advantage: positive means we are closer (or would be sooner in typical play)
            adv = (opp_d - self_d)
            key = (adv, -self_d, -((rx + ry + ti) & 1))
            if best_adv is None or key > best_adv:
                best_adv = key
                best_self_d = self_d
        # Combine: primary by possession advantage, then keep some distance from opponent.
        v = (best_adv[0], -best_self_d, opp_here, parity)
        if best_val is None or v > best_val:
            best_val = v
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]
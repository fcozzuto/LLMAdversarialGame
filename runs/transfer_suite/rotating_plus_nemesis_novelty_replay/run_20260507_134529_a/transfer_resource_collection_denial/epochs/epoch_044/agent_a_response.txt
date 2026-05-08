def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def eval_state(px, py):
        if not resources:
            # No resources visible: flee with obstacle-aware dist
            d = cheb(px, py, ox, oy)
            return (d, -px, -py, 0)
        best_adv = -10**18
        best_closer = 10**18
        best_sec = -10**18
        best_rx, best_ry = 0, 0
        for rx, ry in resources:
            ds = cheb(px, py, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds  # positive => we are closer
            # Prefer first: secure reachable advantage; second: how much; third: deterministic id
            if adv > best_adv or (adv == best_adv and (ds < best_closer or (ds == best_closer and (rx < best_rx or (rx == best_rx and ry < best_ry))))):
                best_adv = adv
                best_closer = ds
                best_sec = adv
                best_rx, best_ry = rx, ry
        # If we can't out-race any resource (best_adv<=0), shift to nearest while also increasing distance from opponent to reduce denials
        if best_adv <= 0:
            # nearest resource priority + distance-from-opponent penalty (deterministic)
            near_d = best_closer
            dist_opp = cheb(px, py, ox, oy)
            return (dist_opp, -near_d, -px, -py)
        # Out-racing possible: maximize advantage, then prefer shorter ds, then flee slightly to prevent swap
        ds = best_closer
        dist_opp = cheb(px, py, ox, oy)
        return (best_adv, -ds, dist_opp, -px - py)

    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        val = eval_state(nx, ny)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]
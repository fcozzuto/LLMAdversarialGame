def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    valid = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                valid.append((dx, dy))
    if not valid:
        return [0, 0]

    if not resources:
        best = None
        best_key = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            dopp = abs(nx - ox) + abs(ny - oy)
            # Pursue to maximize denial pressure when no resources remain
            key = (dopp, abs(nx - sx) + abs(ny - sy))
            if best_key is None or key < best_key:
                best_key = key
                best = (dx, dy)
        return [best[0], best[1]]

    opp_to_res = []
    for rx, ry in resources:
        opp_to_res.append((abs(ox - rx) + abs(oy - ry), rx, ry))
    min_opp_d = min(d for d, _, _ in opp_to_res)

    best = None
    best_key = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        self_adv_best = None  # best resource where we are at least as close as opponent
        self_best_d = None
        self_best_rxry = None
        for rx, ry in resources:
            dself = abs(nx - rx) + abs(ny - ry)
            dopp = abs(ox - rx) + abs(oy - ry)
            if dself <= dopp:
                adv = dopp - dself
                if self_adv_best is None or adv > self_adv_best or (adv == self_adv_best and dself < self_best_d):
                    self_adv_best = adv
                    self_best_d = dself
                    self_best_rxry = (rx, ry)

        # If we can claim a resource earlier/equal, prioritize greatest advantage and closeness.
        # Otherwise, reduce opponent's best available resource distance (deny).
        if self_adv_best is not None:
            # key: maximize advantage -> minimize negative advantage; then minimize self distance
            # tie-breaker: prefer moves that also reduce our distance to opponent (keeps control)
            dopp_after = min_opp_d
            key = (-self_adv_best, self_best_d, abs(nx - ox) + abs(ny - oy), dx, dy)
        else:
            # Denial: minimize opponent nearest-resource distance from the state after our move
            # (our move doesn't change opponent distances, but it changes our future; still useful tie-breaker)
            # Secondary: minimize our nearest resource distance to avoid falling behind.
            min_self_d = min(abs(nx - rx) + abs(ny - ry) for rx, ry in resources)
            key = (0, min_self_d, min_opp_d, abs(nx - ox) + abs(ny - oy), dx, dy)

        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    return [best[0], best[1]]
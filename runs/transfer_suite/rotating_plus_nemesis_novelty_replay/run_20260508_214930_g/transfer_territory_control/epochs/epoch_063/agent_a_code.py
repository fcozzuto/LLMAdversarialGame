def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def border_bias(x, y):
        # Favor edges on our side to counter edge-claim (deterministic, no randomness)
        d_to_top = y
        d_to_bottom = (h - 1) - y
        d_to_left = x
        d_to_right = (w - 1) - x
        # prefer the border farther from opponent's x/y to claim "our" edge
        return min(d_to_left, d_to_right) + min(d_to_top, d_to_bottom)

    # Choose a deterministic target: unclaimed cell that maximizes advantage = (opp_dist - my_dist) with light border preference
    base = abs(sx - ox) + abs(sy - oy)
    best_target = (sx, sy)
    best_adv = -10**18
    candidates = list(unclaimed)
    if not candidates:
        candidates = list(self_t | (unclaimed or set()))
    for tx, ty in candidates:
        if not ok(tx, ty) and (tx, ty) not in self_t and (tx, ty) not in opp_t:
            continue
        myd = abs(tx - sx) + abs(ty - sy)
        oppd = abs(tx - ox) + abs(ty - oy)
        adv = (oppd - myd) * 3 + border_bias(tx, ty) * 0.05
        if (tx, ty) in opp_t:
            adv -= 3.0  # don't target opponent cells unless needed
        if (tx, ty) in self_t:
            adv += 0.5
        if adv > best_adv or (adv == best_adv and (ty, tx) < (best_target[1], best_target[0])):
            best_adv = adv
            best_target = (tx, ty)

    tx, ty = best_target
    best_move = (0, 0)
    best_score = -10**18

    for ddx, ddy in dirs:
        nx, ny = sx + ddx, sy + ddy
        if not ok(nx, ny):
            continue

        score = 0.0
        # Main: move closer to chosen target
        score += (abs(tx - sx) + abs(ty - sy) - (abs(tx - nx) + abs(ty - ny))) * 6.0

        # Territory incentives
        if (nx, ny) in opp_t:
            # flipping on entry: only do it if it also improves target distance
            score += 120.0
            score -= base * 0.02
        elif (nx, ny) in unclaimed:
            score += 55.0
        elif (nx, ny) in self_t:
            score += 12.0

        # Edge pressure: prefer cells that move toward the edge opposite to opponent's nearest border
        score += (min(nx, (w - 1) - nx) + min(ny, (h - 1) - ny)) * 0.15

        # Avoid stepping into opponent territory if equally good but less improving
        if (nx, ny) in opp_t:
            score -= (abs(nx - ox) + abs(ny - oy)) * 0.02

        if score > best_score or (score == best_score and (ddy, ddx) < (best_move[1], best_move[0])):
            best_score = score
            best_move = (ddx, ddy)

    return [int(best_move[0]), int(best_move[1])]
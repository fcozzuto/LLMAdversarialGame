def choose_move(observation):
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    blocked = set()
    for b in obstacles:
        try:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))
        except:
            pass

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    res = []
    for r in resources:
        try:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                res.append((rx, ry))
        except:
            pass
    if not res:
        return [0, 0]

    # Choose our action by maximizing advantage to a race target after 1 step.
    # Advantage = opponent_cheb - our_cheb (bigger means we arrive sooner).
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = -10**9

    # Opponent's likely nearest resource (used to "shadow" it when we can't win races).
    opp_target = min(res, key=lambda t: cheb(ox, oy, t[0], t[1]))

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            continue

        # Pick the best target for us relative to opponent from this hypothetical next position.
        our_dist_best = 10**9
        opp_adv_best = -10**9
        target_for_score = res[0]
        for rx, ry in res:
            ourd = cheb(nx, ny, rx, ry)
            oppd = cheb(ox, oy, rx, ry)
            adv = oppd - ourd
            if adv > opp_adv_best or (adv == opp_adv_best and ourd < our_dist_best):
                opp_adv_best = adv
                our_dist_best = ourd
                target_for_score = (rx, ry)

        # If we can't secure a positive lead, aim closer to the opponent's nearest resource to disrupt timing.
        if opp_adv_best < 0:
            disruption = -cheb(nx, ny, opp_target[0], opp_target[1])
            race_term = -cheb(nx, ny, target_for_score[0], target_for_score[1])
            val = (1000 * opp_adv_best) + disruption + race_term
        else:
            # Strongly prefer winning races (positive lead), then closer arrival.
            val = (1000 * opp_adv_best) - (10 * cheb(nx, ny, target_for_score[0], target_for_score[1]))

        # Deterministic tie-break: smaller dx, then smaller dy.
        if val > best_val or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = val
            best_move = [dx, dy]

    return best_move
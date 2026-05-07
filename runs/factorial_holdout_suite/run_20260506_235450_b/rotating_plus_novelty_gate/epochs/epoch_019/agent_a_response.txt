def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((p[0], p[1]))

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    opp_best = []
    for rx, ry in resources:
        opp_best.append((man(ox, oy, rx, ry), rx, ry))
    opp_best.sort()
    opp_target = opp_best[0][1], opp_best[0][2]

    best_move = [0, 0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue

        local_best_adv = -10**9
        local_best_myd = 10**9
        local_best_opd = 10**9
        for rx, ry in resources:
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)
            adv = opd - myd  # positive means we are closer
            if adv > local_best_adv or (adv == local_best_adv and myd < local_best_myd):
                local_best_adv = adv
                local_best_myd = myd
                local_best_opd = opd

        # If we can reach the chosen opponent target with advantage, prioritize it
        tx, ty = opp_target
        t_myd = man(nx, ny, tx, ty)
        t_opd = man(ox, oy, tx, ty)
        target_adv = t_opd - t_myd

        # Score: maximize advantage, then minimize our distance, then slightly prefer moves that also reduce opponent distance
        score = (local_best_adv * 1000) + (-local_best_myd) + (-(local_best_opd - local_best_myd) if target_adv > 0 else 0) + (-abs(nx - tx) - abs(ny - ty)) * 0.01
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
        elif score == best_score:
            # deterministic tie-break: prefer staying if equal; else smaller dx^2+dy^2
            cur_norm = best_move[0] * best_move[0] + best_move[1] * best_move[1]
            new_norm = dx * dx + dy * dy
            if new_norm < cur_norm or (new_norm == cur_norm and (dx, dy) == (0, 0)):
                best_move = [dx, dy]

    return best_move
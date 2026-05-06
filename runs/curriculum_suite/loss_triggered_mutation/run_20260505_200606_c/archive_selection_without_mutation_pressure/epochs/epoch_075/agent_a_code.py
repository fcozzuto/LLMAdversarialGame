def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = {(p[0], p[1]) for p in obs_list if p is not None and len(p) >= 2}
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # one-step lookahead: pick move that maximizes the best "resource lead"
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        best_lead = None
        best_ourd = None
        best_near_d = None

        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ourd = cheb(nx, ny, rx, ry)
            oppd = cheb(ox, oy, rx, ry)
            lead = oppd - ourd
            neard = ourd  # already cheb
            if (best_lead is None or lead > best_lead or
                (lead == best_lead and (neard < best_near_d or
                                        (neard == best_near_d and ourd < best_ourd)))):
                best_lead = lead
                best_ourd = ourd
                best_near_d = neard

        # Encourage taking resources when possible (lead >= 0), otherwise minimize our distance to the best target
        # Key: higher lead first, then smaller our distance, then smaller opponent distance to that resource (safer denial)
        if best_near_d is None:
            continue
        # recompute opp distance to the chosen best target deterministically
        chosen_rx, chosen_ry = None, None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ourd = cheb(nx, ny, rx, ry)
            oppd = cheb(ox, oy, rx, ry)
            lead = oppd - ourd
            if lead == best_lead and ourd == best_near_d:
                chosen_rx, chosen_ry = rx, ry
                break
        oppd_chosen = cheb(ox, oy, chosen_rx, chosen_ry) if chosen_rx is not None else 10**9

        key = (-best_lead, best_ourd, oppd_chosen, dx, dy)  # invert lead by using negative for min-lex
        if best is None or key < best[0]:
            best = (key, [dx, dy])

    return best[1] if best else [0, 0]
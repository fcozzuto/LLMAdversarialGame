def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best = None
    best_key = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0

        # "Control" heuristic: prioritize the resource where we can most improve relative arrival time,
        # but also value moving toward the most contested resource overall.
        best_adv = -10**9
        best_myd = 10**9
        best_contest = -10**9
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = opd - myd  # positive => we are closer (good)
            if adv > best_adv or (adv == best_adv and myd < best_myd):
                best_adv = adv
                best_myd = myd
            # Contest pressure: how "unfair" the race is right now from our prospective position.
            contest = myd - opd  # negative => we are closer
            if (-contest) > best_contest:
                best_contest = -contest

        # Primary: maximize best_adv, Secondary: minimize best_myd, Tertiary: reduce our distance to opponent
        # (prevents being kited into losing races).
        key = (-best_adv, best_myd, cheb(nx, ny, ox, oy), nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    return best if best is not None else [0, 0]
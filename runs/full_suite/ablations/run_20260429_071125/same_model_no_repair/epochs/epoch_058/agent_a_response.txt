def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    live_res = [(x, y) for (x, y) in resources if (x, y) not in obstacles]
    if not live_res:
        # Deterministic retreat: move to maximize distance from opponent.
        best = max(legal, key=lambda t: (cheb(t[2], t[3], ox, oy), -t[0], -t[1]))
        return [best[0], best[1]]

    # If resources are few, prioritize fastest finish; else prioritize contests & blocking.
    rleft = observation.get("remaining_resource_count", len(live_res))
    finish_mode = (rleft <= 4)

    best_move = None
    best_val = -10**18
    for dx, dy, nx, ny in legal:
        my_opp_dist = cheb(nx, ny, ox, oy)

        # Value is driven by best resource under a contest model.
        # If we can be closer than opponent, we aggressively take it and also
        # try to keep the opponent farther from it.
        # Otherwise, we keep some separation and still move toward the closest resource.
        best_contest = -10**18
        best_fallback = -10**18
        for rx, ry in live_res:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = opd - myd  # positive => we are closer next to this resource

            # Blocking-like term: prefer positions that also make opponent's path to this resource longer.
            block = opd - myd

            if finish_mode:
                # Race: minimize our distance strongly, break ties by maximizing separation from opponent.
                val = (-myd * 8) + (adv * 3) + (my_opp_dist * 0.5) + (block * 1.5)
            else:
                # Contest: strong reward for being closer; if not, only mild reward for progress.
                val = (adv * 12) - (myd * 2) + (opd * -0.5) + (block * 1.2)
            if val > best_contest:
                best_contest = val

            # Fallback when no contest: just approach nearest resource while staying away from opponent.
            fb = (-myd * 3) + (my_opp_dist * 1.0)
            if fb > best_fallback:
                best_fallback = fb

        # Decide between contest and fallback based on whether any contest looks favorable.
        # If best_contest isn't actually positive enough, we blend toward fallback.
        mix = 0.7 if best_contest > 0 else 0.35
        score = mix * best_contest + (1 - mix) * best_fallback

        # Deterministic tie-break: lower dx, then lower dy, then staying still preferred.
        key = (score,
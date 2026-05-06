def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def md(ax, ay, bx, by):
        ax -= bx
        ay -= by
        if ax < 0:
            ax = -ax
        if ay < 0:
            ay = -ay
        return ax + ay

    # Quick target ranking from current positions: prefer resources where we can beat opponent.
    ranked = []
    for rx, ry in resources:
        d_our = md(sx, sy, rx, ry)
        d_opp = md(ox, oy, rx, ry)
        margin = d_opp - d_our
        # Strongly favor direct win (we no worse than opponent), then larger margin, then closer resource.
        ranked.append((-(1 if margin >= 0 else 0), -margin, d_our, rx, ry))
    ranked.sort()
    top = ranked[:6] if len(ranked) > 6 else ranked

    best_val = None
    best_move = (0, 0)

    # Evaluate best candidate resource for each potential move; add obstacle avoidance and mild preference for staying on a resource.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        val = -10**18
        # If we step onto a resource, it should be very strong.
        on_res = 0
        for rx, ry in resources:
            if rx == nx and ry == ny:
                on_res = 1
                break
        if on_res:
            val = 10**12
        else:
            # Local lookahead on a few top resources.
            for _, _, _, rx, ry in top:
                d_our = md(nx, ny, rx, ry)
                d_opp = md(ox, oy, rx, ry)
                margin = d_opp - d_our

                # Prefer moves that improve (margin), then reduce our distance, then increase opponent distance.
                score = 0
                if margin >= 0:
                    score += 2000
                score += int(margin * 100)
                score -= d_our * 3
                score += d_opp * 1

                # Discourage moving away from the best currently contested resource.
                # (Small penalty if we significantly increase our distance to that resource.)
                d_our_now = md(sx, sy, rx, ry)
                if d_our > d_our_now:
                    score -= (d_our - d_our_now) * 6

                # Light bias toward edges that opponent is likely avoiding (safe collector tends to hug resources).
                if nx == 0 or ny == 0 or nx == w - 1 or ny == h - 1:
                    score += 8

                if score > val:
                    val = score

        # Deterministic tie-break: prefer (dx,dy) closer to opponent along x then y? Use fixed order by sum then lex.
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)
        elif val == best_val:
            # tie-break: prefer staying still last, then smaller dx abs, then smaller dy abs, then lex.
            def tkey(m):
                ddx, ddy = m
                return (1 if (ddx == 0 and ddy == 0) else 0, abs(ddx), abs(ddy), ddx, ddy)
            if tkey((dx, dy)) < tkey(best_move):
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
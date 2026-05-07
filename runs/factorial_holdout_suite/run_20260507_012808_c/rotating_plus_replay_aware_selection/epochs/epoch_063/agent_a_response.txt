def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d(x1, y1, x2, y2):
        return max(abs(x2 - x1), abs(y2 - y1))

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [dx, dy]
        return [0, 0]

    # New strategy: directly maximize expected collection advantage after this move
    best = (float("-inf"), 0, 0)
    for mx, my in dirs:
        nx, ny = sx + mx, sy + my
        if not valid(nx, ny):
            continue

        cur_score = 0.0
        nearest_self = 10**9
        nearest_opp = 10**9
        for rx, ry in resources:
            ds = d(nx, ny, rx, ry)
            do = d(ox, oy, rx, ry)
            nearest_self = ds if ds < nearest_self else nearest_self
            nearest_opp = do if do < nearest_opp else nearest_opp

            # Advantage term: prefer resources where we can arrive earlier than opponent
            adv = do - ds
            if adv > 0:
                cur_score += 6.0 * adv + 2.0 / (1 + ds)
            else:
                # If opponent is earlier/tied, strongly discourage unless very close for us
                cur_score += 0.2 * adv - 0.4 * ds / (1 + do)

        # Additional deterministic tie-breaks
        # Prefer being closer than opponent's nearest target, then closer overall
        if nearest_self < nearest_opp:
            cur_score += 4.0
        cur_score -= 0.05 * nearest_self

        if cur_score > best[0] or (cur_score == best[0] and (mx, my) < (best[1], best[2])):
            best = (cur_score, mx, my)

    return [best[1], best[2]]
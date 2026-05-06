def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            x, y = o[0], o[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    res_list = res

    def best_adv(px, py, oppx, oppy):
        best = (-10**12, None)
        for tx, ty in res_list:
            myd = md(px, py, tx, ty)
            opd = md(oppx, oppy, tx, ty)
            # prefer resources we can reach earlier; otherwise still prefer blocking-like proximity
            advantage = (opd - myd) * 5 - myd
            # slight preference for being closer to center of resource set
            cx = sum(p[0] for p in res_list) / len(res_list)
            cy = sum(p[1] for p in res_list) / len(res_list)
            advantage -= (0.03 * (md(px, py, int(cx), int(cy))))
            if (tx, ty) == min(res_list, key=lambda p: (md(oppx, oppy, p[0], p[1]), p[0], p[1])):
                advantage += 3
            if advantage > best[0] or (advantage == best[0] and (tx, ty) < best[1]):
                best = (advantage, (tx, ty))
        return best[0], best[1]

    # choose move by 1-step lookahead: maximize our best achievable advantage while discouraging opponent gains
    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_val = -10**18

    # precompute opponent "nearest_resource" target for defense
    opp_target = min(res_list, key=lambda p: (md(ox, oy, p[0], p[1]), p[0], p[1]))
    opp_t_dist = md(ox, oy, opp_target[0], opp_target[1])

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            nx, ny = sx, sy  # engine would keep in place
        myd_to_opp_t = md(nx, ny, opp_target[0], opp_target[1])
        # estimate opponent next: if it keeps chasing nearest resource, its distance should drop by at most 2
        opp_next_est = max(0, opp_t_dist - 2)
        # evaluate our advantage to any resource; and penalize letting opponent reduce their chase gap
        adv, tgt = best_adv(nx, ny, ox, oy)
        defense = 0
        if tgt == opp_target:
            # being able to match/beat opponent on its target is strong
            defense = (opp_next_est - myd_to_opp_t) * 7
        # also consider general "denial": reduce opponent's advantage to their target by moving closer (even if not exact target)
        defense -= max(0, md(nx, ny, opp_target[0], opp_target[1]) - myd_to_opp_t)  # deterministic no-op
        val = adv + defense
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
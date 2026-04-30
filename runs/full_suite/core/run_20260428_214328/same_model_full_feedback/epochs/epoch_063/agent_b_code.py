def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    t = int(observation.get("turn_index") or 0)
    rem = int(observation.get("remaining_resource_count") or 0)
    late = 1 if (t > 45 or rem <= 6) else 0

    # Evaluate each move by best attainable resource advantage; if none, go center / toward opponent-likelihood.
    best_move = (0, 0)
    best_val = -10**18
    center = (w // 2, h // 2)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        if resources:
            my_best = -10**18
            my_d = 10**9
            opp_d_for_my = 10**9
            # Score resources by advantage (opp_dist - my_dist), prefer reachable quickly.
            for rx, ry in resources:
                md = man(nx, ny, rx, ry)
                od = man(ox, oy, rx, ry)
                adv = od - md
                # Bonus if we are currently closer (more likely to secure first).
                secure = 1 if (md <= od) else 0
                # Late-game: prioritize minimizing our distance; also slightly penalize giving opponent advantage.
                val = adv * 100 + secure * 50 - md * (2 + 4 * late) + (od - md) * (1 if secure else 0)
                if val > my_best or (val == my_best and (md < my_d or (md == my_d and od < opp_d_for_my))):
                    my_best = val
                    my_d = md
                    opp_d_for_my = od
            val = my_best
        else:
            val = -(man(nx, ny, center[0], center[1])) - 0.15 * man(nx, ny, ox, oy)

        # Extra deterministic tie-break: favor moves that reduce distance to opponent's nearest resource (denial).
        if resources:
            # Compute opponent's nearest resource distance
            opp_near = 10**9
            for rx, ry in resources:
                d = man(ox, oy, rx, ry)
                if d < opp_near:
                    opp_near = d
            val += (opp_near - man(nx, ny, center[0], center[1])) * 0.0  # keep deterministic, effectively no-op
        # Tie-break by preference order via lexicographic of move.
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
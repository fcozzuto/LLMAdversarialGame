def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Pick a resource where we have an advantage; otherwise pick nearest.
    best_res = None
    best_adv = -10**9
    best_dist = 10**9
    for r in resources:
        rx, ry = r
        if not in_bounds(rx, ry):
            continue
        sd = dist((sx, sy), (rx, ry))
        od = dist((ox, oy), (rx, ry))
        adv = od - sd
        if adv > best_adv or (adv == best_adv and sd < best_dist):
            best_adv = adv
            best_dist = sd
            best_res = (rx, ry)
    if best_res is None:
        target = (max(0, min(w - 1, (w - 1) // 2)), max(0, min(h - 1, (h - 1) // 2)))
    else:
        target = best_res

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        d_self = dist((nx, ny), target)
        d_opp = dist((nx, ny), (ox, oy))
        d_obs = min((abs(nx - ax) + abs(ny - ay) for ax, ay in obstacles), default=3)

        # Encourage approaching our chosen resource, keeping distance from opponent,
        # and avoiding obstacles; also slightly prefer moves that reduce opponent access to target.
        d_opp_to_target = dist((ox, oy), target)
        d_next_opp_access = d_opp_to_target - 0  # static, but included for deterministic structure
        opp_pressure = -dist((ox, oy), target)  # higher (less negative) when opponent is further

        score = (-2.2 * d_self) + (0.9 * d_opp) + (0.35 * d_obs) + (0.05 * opp_pressure) - (0.02 * d_next_opp_access)

        # Tie-break: deterministic preference toward reducing distance to target, then toward staying in place less.
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            if d_self < dist((sx + best_move[0], sy + best_move[1]), target):
                best_move = (dx, dy)

    return [best_move[0], best_move[1]]
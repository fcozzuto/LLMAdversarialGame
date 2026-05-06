def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    res = [tuple(r) for r in resources]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Pick a few resources most relevant to opponent (for denial/intercept behavior).
    scored_res = []
    for rx, ry in res:
        od = man(ox, oy, rx, ry)
        scored_res.append((od, rx, ry))
    scored_res.sort(key=lambda t: (t[0], t[1], t[2]))
    targets = [(rx, ry) for _, rx, ry in scored_res[:min(4, len(scored_res))]] or res

    # Also keep our own nearby resources as fallback.
    my_sorted = sorted(res, key=lambda p: (man(x, y, p[0], p[1]), p[0], p[1]))
    fallback_targets = my_sorted[:min(3, len(my_sorted))]

    best = (-10**18, 0, 0)
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not ok(nx, ny):
            continue

        # Primary: maximize ability to reach resources before opponent.
        best_target_score = -10**18
        for rx, ry in targets:
            our_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            # Prefer moves that reduce opp's lead and improve our approach.
            s = (opp_d - our_d) * 10 - our_d
            # Slightly bias toward closer targets in general.
            s -= 0.2 * (opp_d)
            # If the resource is far, don't overcommit; still allow if we can swing parity.
            if opp_d > 10 and our_d > 10 and (opp_d - our_d) < 3:
                s -= 5
            if s > best_target_score:
                best_target_score = s

        # Secondary: if no good denial angle, just advance to our closest resource.
        fb_score = -10**18
        for rx, ry in fallback_targets:
            our_d = man(nx, ny, rx, ry)
            fb_score = max(fb_score, -our_d)

        # Combine; denial is primary. If denial scores tie, prefer advancing.
        total = best_target_score + 0.5 * fb_score
        # Deterministic tie-break: lexicographically smallest move among equals.
        if total > best[0] or (total == best[0] and (dx, dy) < (best[1], best[2])):
            best = (total, dx, dy)

    return [best[1], best[2]]
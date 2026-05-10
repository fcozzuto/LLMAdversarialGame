def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs_set = {(p[0], p[1]) for p in obstacles}
    role = (observation.get("self_role") or "pursuer").lower()

    cands = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    nearest_opp_corner = min(corners, key=lambda c: man(ox, oy, c[0], c[1]))
    nearest_opp_corner_dist = man(ox, oy, nearest_opp_corner[0], nearest_opp_corner[1])

    def obstacle_clearance(x, y):
        if not obs_set:
            return 6
        d = min(abs(x - ax) + abs(y - ay) for (ax, ay) in obs_set)
        return d if d < 6 else 6

    sign = 1.0 if role == "pursuer" else -1.0
    best = (-10**9, 0, 0)
    order = 0
    for dx, dy in cands:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs_set:
            order += 1
            continue

        d_opp = man(nx, ny, ox, oy)

        # Pursuer tries to "cut off" toward opponent's nearest corner; evader tries the opposite.
        corner_progress = nearest_opp_corner_dist - man(ox, oy, nearest_opp_corner[0], nearest_opp_corner[1])
        # Actually use how much closer we get to the opponent's corner.
        our_to_corner = man(nx, ny, nearest_opp_corner[0], nearest_opp_corner[1])
        opp_to_corner = man(ox, oy, nearest_opp_corner[0], nearest_opp_corner[1])
        cutoff = (opp_to_corner - our_to_corner)

        align = -max(abs(nx - ox), abs(ny - oy))  # favor moving toward/keeping contact

        clear = obstacle_clearance(nx, ny)

        if role == "pursuer":
            # Minimize distance, maximize cutoff and safety.
            score = (-d_opp) + 0.55 * cutoff + 0.18 * align + 0.12 * clear
        else:
            # Maximize distance, try to worsen cutoff, prefer safety.
            score = (d_opp) - 0.50 * cutoff - 0.12 * align + 0.12 * clear + 0.02 * corner_progress

        # Deterministic tie-breaker: fixed iteration order.
        cand = (score, -order, dx, dy)
        if cand > best:
            best = cand
        order += 1

    return [best[2], best[3]]
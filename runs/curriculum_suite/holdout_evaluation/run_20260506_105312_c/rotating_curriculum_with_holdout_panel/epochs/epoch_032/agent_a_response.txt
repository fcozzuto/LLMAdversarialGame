def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Identify a "danger" resource where opponent is currently closer (strictly).
    danger = []
    best_my = 10**9
    for rx, ry in resources:
        d = cheb(sx, sy, rx, ry)
        if d < best_my: best_my = d
    for rx, ry in resources:
        d_me = cheb(sx, sy, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        if d_me <= best_my + 0 and d_op < d_me:
            danger.append((rx, ry))

    best_move = None
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue

        own_min_now = 10**9
        own_min_after = 10**9
        best_adv = -10**18  # maximize (opp_dist - new_dist) to some resource
        for rx, ry in resources:
            d_now = cheb(sx, sy, rx, ry)
            d_new = cheb(nx, ny, rx, ry)
            if d_now < own_min_now: own_min_now = d_now
            if d_new < own_min_after: own_min_after = d_new
            d_op = cheb(ox, oy, rx, ry)
            adv = d_op - d_new
            if adv > best_adv:
                best_adv = adv

        # If we are in denial mode, prioritize reducing distance to a danger resource and
        # making our best-advantage resource even stronger.
        if danger:
            d_to_danger = 10**9
            for rx, ry in danger:
                d_to_danger = min(d_to_danger, cheb(nx, ny, rx, ry))
            score = (best_adv * 10) + (own_min_now - own_min_after) * 5 - d_to_danger * 2
        else:
            score = (best_adv * 10) + (own_min_now - own_min_after) * 6 - own_min_after

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]
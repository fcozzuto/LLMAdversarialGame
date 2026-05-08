def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # One-step lookahead: pick the move that maximizes current distance-based lead to the best resource.
    best = None
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < gw and 0 <= ny < gh):  # invalid move -> engine keeps in place; we avoid it deterministically
            continue
        if (nx, ny) in obstacles:
            continue

        # compute best resource target from this new position
        # advantage = opponent_dist - self_dist (higher is better)
        best_adv = None
        best_sd = None
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd
            if best_adv is None or adv > best_adv or (adv == best_adv and sd < best_sd):
                best_adv = adv
                best_sd = sd

        # Secondary heuristics:
        # 1) if opponent is already closer to some resource (best_adv < 0), try to reduce self_dist strongly
        # 2) prefer not to step away from center of "resource density": use min self_dist to resources
        # 3) deterministic tie-break by dx,dy order and keeping move small
        min_sd = best_sd
        key = (best_adv, -min_sd, -(abs(dx) + abs(dy)), -dx, -dy)
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]
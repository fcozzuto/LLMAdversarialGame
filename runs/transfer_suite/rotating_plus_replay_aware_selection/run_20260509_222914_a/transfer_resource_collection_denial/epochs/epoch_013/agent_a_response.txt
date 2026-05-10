def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0),  (0, 0),  (1, 0),
              (-1, 1),  (0, 1),  (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = w // 2, h // 2
        best = (10**9, -10**9)
        best_mv = [0, 0]
        for dx0, dy0 in deltas:
            nx, ny = x + dx0, y + dy0
            if nx < 0 or nx >= w or ny < 0 or ny >= h: 
                continue
            if (nx, ny) in obstacles:
                continue
            d = cheb(nx, ny, tx, ty)
            od = cheb(ox, oy, tx, ty)
            sc = (d, -(od - d))
            if sc < best:
                best = sc
                best_mv = [dx0, dy0]
        return best_mv

    turns = observation.get("turns_remaining", 0)
    remaining = observation.get("remaining_resource_count", len(resources))
    # Earlier in game: race more; later: take shortest.
    self_weight = 1.0 + (1.0 if remaining > 6 else 0.2)
    opp_weight = 1.2 if turns > 20 else 1.0

    best_res = None
    best_val = -10**18
    for rx, ry in resources:
        sd = cheb(x, y, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Advantage: prefer resources we can reach sooner (or opponent later).
        val = (opp_weight * od - self_weight * sd)
        # If similar, prefer closer overall to avoid indecision.
        val -= 0.01 * sd
        if val > best_val:
            best_val = val
            best_res = (rx, ry)

    tx, ty = best_res
    best_key = None
    best_mv = [0, 0]
    for dx0, dy0 in deltas:
        nx, ny = x + dx0, y + dy0
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        sd = cheb(nx, ny, tx, ty)
        # Look one step ahead for race advantage.
        od = cheb(ox, oy, tx, ty)
        key = (sd, -(od - sd), dx0, dy0)
        if best_key is None or key < best_key:
            best_key = key
            best_mv = [dx0, dy0]
    return best_mv
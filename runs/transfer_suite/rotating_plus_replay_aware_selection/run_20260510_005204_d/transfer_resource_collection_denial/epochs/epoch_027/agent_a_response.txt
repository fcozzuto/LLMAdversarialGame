def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Choose target with best chance to arrive earlier than opponent
    best_rx, best_ry = resources[0]
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        adv = opd - myd
        center = -(abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0))
        key = (adv >= 0, adv, -myd, center, -(rx + ry))
        if best_key is None or key > best_key:
            best_key = key
            best_rx, best_ry = rx, ry

    tx, ty = best_rx, best_ry

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cur_myd = cheb(sx, sy, tx, ty)
    cur_opd_to_cell = cheb(ox, oy, sx, sy)

    best_move = [0, 0]
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        myd_next = cheb(nx, ny, tx, ty)
        # Prefer improving our arrival time; discourage moving closer to opponent unless it helps the target race
        opd_current_to_target = cheb(ox, oy, tx, ty)
        adv_next = opd_current_to_target - myd_next

        dist_improve = cur_myd - myd_next  # positive if closer
        opp_closeness = cheb(ox, oy, nx, ny) - cur_opd_to_cell  # positive if we increase distance

        # If we are not currently favored, require meaningful improvement to cross the tie
        favor_gate = 0
        if cheb(ox, oy, tx, ty) - cur_myd < 0 and dist_improve < 0:
            favor_gate = -1

        val = (adv_next >= 0, adv_next, dist_improve, opp_closeness, -(myd_next), -abs(nx - tx) - abs(ny - ty), -favor_gate)
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move
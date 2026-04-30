def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = {(p[0], p[1]) for p in obstacles}

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]
    resources = [(rx, ry) for (rx, ry) in resources if (rx, ry) not in obs]
    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    for rx, ry in resources:
        if rx == sx and ry == sy:
            return [0, 0]

    # Pick a target deterministically; if we have no immediate advantage, grab the resource that minimizes our loss.
    best_t = None
    best_score = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        advantage = od - myd  # positive: we are closer
        # Prefer positive advantage; otherwise minimize how far behind we are.
        score = (0 if advantage > 0 else 1, -advantage if advantage > 0 else myd - od, myd, rx, ry)
        if best_score is None or score < best_score:
            best_score = score
            best_t = (rx, ry)
    tx, ty = best_t

    # Move: approach target while keeping distance from opponent and not walking into near-obstacle "friction".
    def near_obstacle(x, y):
        # small penalty if adjacent to obstacle (helps avoid getting stuck around corners)
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in obs:
                    return 1
        return 0

    best_move = (0, 0)
    best_obj = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obs:
            continue
        myd_next = cheb(nx, ny, tx, ty)
        od_next = cheb(ox, oy, tx, ty)
        # Objective: minimize who will be closer to the target after our move; then maximize distance from opponent; then reduce obstacle friction.
        dist_opp = cheb(nx, ny, ox, oy)
        obj = (myd_next - od_next, myd_next, -dist_opp, near_obstacle(nx, ny), rx_s := tx, ry_s := ty)
        if best_obj is None or obj < best_obj:
            best_obj = obj
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
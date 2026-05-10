def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    res = []
    resset = set()
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            res.append((rx, ry))
            resset.add((rx, ry))

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def cd(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = [0, 0]
    best_val = -10**18

    if res:
        for dx0, dy0 in deltas:
            nx, ny = x + dx0, y + dy0
            if not inb(nx, ny):
                continue
            # If we can pick immediately, do it.
            if (nx, ny) in resset:
                return [dx0, dy0]

            # For each visible resource, measure how much we can beat/deny opponent.
            # Choose move that maximizes (opp_dist - self_dist) to the best target,
            # with small tie-break favoring shorter self_dist.
            best_target_gain = -10**18
            best_target_self = 10**18
            for rx, ry in res:
                sd = cd(nx, ny, rx, ry)
                od = cd(ox, oy, rx, ry)
                gain = od - sd
                if gain > best_target_gain or (gain == best_target_gain and sd < best_target_self):
                    best_target_gain = gain
                    best_target_self = sd

            # Also discourage moving closer to obstacles implicitly via inb validity,
            # and slightly discourage giving opponent an easier chase by adding small penalty to distance.
            opp_closeness = cd(nx, ny, ox, oy)
            val = best_target_gain * 1000 - best_target_self - opp_closeness * 0.1
            if val > best_val:
                best_val = val
                best = [dx0, dy0]
        return best

    # If no resources visible, drift to center while keeping away from opponent.
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best_far = -10**18
    for dx0, dy0 in deltas:
        nx, ny = x + dx0, y + dy0
        if not inb(nx, ny):
            continue
        to_center = cd(nx, ny, cx, cy)
        to_opp = cd(nx, ny, ox, oy)
        val = to_opp * 1000 - to_center
        if val > best_far:
            best_far = val
            best = [dx0, dy0]
    return best
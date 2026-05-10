def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation.get("opponent_position") or (None, None)
    obs_list = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obs_list)

    unclaimed = observation.get("unclaimed_cells") or []
    target = None
    best_d = 10**9
    for tx, ty in unclaimed:
        if (tx, ty) in obs:
            continue
        d = abs(tx - sx) + abs(ty - sy)
        if d < best_d or (d == best_d and (tx, ty) < target):
            best_d = d
            target = (tx, ty)

    if target is None:
        self_pos_set = set(observation.get("self_territory") or [])
        opp_pos_set = set(observation.get("opponent_territory") or [])
        if opp_pos_set:
            tx, ty = min(opp_pos_set, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
            target = (tx, ty)
        elif self_pos_set:
            tx, ty = min(self_pos_set, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
            target = (tx, ty)
        else:
            target = (sx, sy)

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = (0, 0)
    best_val = -10**9
    tx, ty = target
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obs:
            continue
        val = - (abs(tx - nx) + abs(ty - ny))
        if ox is not None and oy is not None:
            val += 0.001 * (abs(ox - nx) + abs(oy - ny))
        if val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)
    return [best[0], best[1]]
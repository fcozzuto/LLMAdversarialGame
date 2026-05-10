def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obs_set = {(x, y) for x, y in observation.get("obstacles", [])}
    self_set = {(x, y) for x, y in (observation.get("self_territory") or [])}
    opp_set = {(x, y) for x, y in (observation.get("opponent_territory") or [])}
    unclaimed = observation.get("unclaimed_cells") or []
    options = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_set

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    if unclaimed:
        def target_key(p):
            px, py = p
            return (abs(px - cx) + abs(py - cy), abs(px - sx) + abs(py - sy), px, py)
        tx, ty = min(unclaimed, key=target_key)
    else:
        tx, ty = ox, oy

    best_move = [0, 0]
    best_key = None
    for dx, dy in options:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        hit_opp = (nx, ny) in opp_set
        hit_unclaimed = (nx, ny) in set(unclaimed) if unclaimed else False
        # Prefer stealing, then expanding near chosen target, while lightly reducing opponent proximity
        dist_to_target = abs(tx - nx) + abs(ty - ny)
        dist_to_opp = abs(ox - nx) + abs(oy - ny)
        k = (0 if hit_opp else 1, 0 if hit_unclaimed else 1, dist_to_target, dist_to_opp, nx, ny)
        if best_key is None or k < best_key:
            best_key = k
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]
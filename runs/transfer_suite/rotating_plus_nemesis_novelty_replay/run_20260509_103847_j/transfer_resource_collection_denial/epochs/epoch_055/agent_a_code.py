def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles_list)

    if any((sx == rx and sy == ry) for rx, ry in resources):
        return [0, 0]
    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_move = (None, None, -10**9, 10**9)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        # pick the resource that would be best to pursue from (nx, ny)
        best_key = None
        best_self_d = 10**9
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            # maximize lead (opp closer => smaller ds - do, so use opp_d - self_d)
            key = (do - ds, -ds, rx, ry)
            if best_key is None or key > best_key:
                best_key = key
                best_self_d = ds

        if best_key is None:
            continue

        # Prefer moves that increase lead most; break ties toward faster pickup.
        lead = best_key[0]
        fast = best_self_d
        cand = (dx, dy, lead, fast)
        if cand[2] > best_move[2] or (cand[2] == best_move[2] and cand[3] < best_move[3]):
            best_move = cand

    if best_move[0] is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]
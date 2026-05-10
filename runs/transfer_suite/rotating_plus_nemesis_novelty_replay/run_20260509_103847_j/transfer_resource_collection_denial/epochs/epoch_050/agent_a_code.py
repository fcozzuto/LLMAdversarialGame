def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles_list)

    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Target selection: prefer resources where we are closer; otherwise deny opponent most.
    best = None  # (primary, secondary, rx, ry)
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        primary = (ds - do)  # smaller is better (more self advantage)
        # If we are not advantaged, prefer resources that are close to opponent (deny more effectively).
        if ds <= do:
            secondary = ds
        else:
            secondary = -do  # maximize opponent closeness => minimize -do
        key = (primary, secondary, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))

    tx, ty = best[1]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            ds_next = man(nx, ny, tx, ty)
            do_to_target = man(ox, oy, tx, ty)
            # Move that reduces our distance to target; break ties by not letting opponent gain a lot.
            gain = (man(nx, ny, tx, ty) - man(sx, sy, tx, ty))
            # Also prefer moves that reduce our distance without increasing it much.
            key = (ds_next, abs(gain), nx, ny, -do_to_target)
            candidates.append((key, (dx, dy)))

    if not candidates:
        # If fully blocked, try staying put (engine keeps us in place if invalid).
        return [0, 0]

    candidates.sort(key=lambda t: t[0])
    return list(candidates[0][1])
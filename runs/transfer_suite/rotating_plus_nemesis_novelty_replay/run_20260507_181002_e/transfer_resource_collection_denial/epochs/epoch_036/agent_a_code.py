def choose_move(observation):
    def to_xy(v):
        if isinstance(v, (list, tuple)) and len(v) == 2:
            return int(v[0]), int(v[1])
        return None

    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = to_xy(observation.get("self_position", (0, 0))) or (0, 0)
    ox, oy = to_xy(observation.get("opponent_position", (0, 0))) or (0, 0)

    obs = set()
    for o in observation.get("obstacles", []) or []:
        t = to_xy(o)
        if t:
            x, y = t
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        t = to_xy(r)
        if t:
            x, y = t
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    cur_dist = abs(ox - sx) + abs(oy - sy)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_key = None

    def best_target_from(px, py):
        best = None
        for tx, ty in resources:
            sd = abs(tx - px) + abs(ty - py)
            od = abs(tx - ox) + abs(ty - oy)
            # Prefer targets where we're not worse, and especially where opponent is significantly worse.
            key = (od - sd, -sd)
            if best is None or key > best[0]:
                best = (key, (tx, ty), sd, od)
        return best

    # Prefer moves that reduce our distance to an advantaged target; also avoid getting close to opponent unless beneficial.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        bt = best_target_from(nx, ny)
        if not bt:
            continue
        (margin, neg_sd), (tx, ty), sd, od = bt
        # If we are winning on this target, strongly prefer it; otherwise, try to at least block by going toward their closest-ish resource.
        advantage = margin
        opp_proximity = abs(nx - ox) + abs(ny - oy)
        tie_break = (0 if advantage > 0 else 1, -advantage, sd, opp_proximity)
        # Secondary: slightly prefer moving toward center-ish to reduce edge traps.
        center = -(abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2))
        key = (0 if advantage > 0 else 1, -advantage, sd, opp_proximity, -center, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
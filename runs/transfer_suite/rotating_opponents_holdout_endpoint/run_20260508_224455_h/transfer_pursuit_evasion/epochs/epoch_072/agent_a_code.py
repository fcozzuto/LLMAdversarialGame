def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = str(observation.get("self_role") or "")
    is_pursuer = ("pursu" in role.lower()) or ("chase" in role.lower()) or ("capt" in role.lower())
    is_evader = ("evad" in role.lower()) or ("escap" in role.lower())
    if not is_pursuer and not is_evader:
        is_evader = True

    obs_set = set()
    for p in observation.get("obstacles") or []:
        try:
            if isinstance(p, dict):
                x, y = int(p.get("x", -1)), int(p.get("y", -1))
            else:
                x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))
        except Exception:
            pass

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs_set:
            continue
        d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        score = -d2 if is_pursuer else d2
        if best is None or score > best_score:
            best = (dx, dy)
            best_score = score
    if best is None:
        return [0, 0]
    return [best[0], best[1]]
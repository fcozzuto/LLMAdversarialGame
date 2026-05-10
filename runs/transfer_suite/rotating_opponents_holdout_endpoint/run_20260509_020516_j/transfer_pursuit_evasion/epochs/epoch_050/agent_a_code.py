def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for it in observation.get("obstacles") or []:
        if isinstance(it, dict):
            x, y = it.get("x"), it.get("y")
        else:
            x, y = it[0], it[1]
        if x is None or y is None:
            continue
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    is_evader = any(k in role for k in ("evader", "runner", "escape", "evasion"))
    is_chaser = any(k in role for k in ("pursuer", "chaser", "catcher"))
    if not is_evader and not is_chaser:
        is_evader = False
    want_away = is_evader and not is_chaser

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        val = -d2 if want_away else d2  # maximize val
        if best is None or val > best_val:
            best, best_val = [dx, dy], val

    if best is not None:
        return best
    return [0, 0]
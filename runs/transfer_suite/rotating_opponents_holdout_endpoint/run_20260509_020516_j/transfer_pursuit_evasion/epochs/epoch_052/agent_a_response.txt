def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for it in observation.get("obstacles") or []:
        try:
            if isinstance(it, dict):
                x, y = it.get("x"), it.get("y")
            else:
                x, y = it[0], it[1]
            if x is None or y is None:
                continue
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            continue

    role = (observation.get("self_role") or "").lower()
    is_evader = any(k in role for k in ("evader", "runner", "escape", "evasion"))
    is_pursuer = any(k in role for k in ("pursuer", "chaser", "catcher"))
    if not is_evader and not is_pursuer:
        is_evader = False
        is_pursuer = False

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        # Greedy: evader maximizes distance; pursuer minimizes distance.
        if is_evader:
            score = d2
        elif is_pursuer:
            score = -d2
        else:
            # Unknown role: default to evasion if already far, otherwise chase.
            dcur = (sx - ox) * (sx - ox) + (sy - oy) * (sy - oy)
            score = d2 if dcur > (w * h) // 4 else -d2

        # Extra tie-breaker: avoid moving into lines/corners poorly by preferring smaller lexicographic move.
        move_key = (score, -nx, -ny, dx, dy) if is_evader else (score, nx, ny, dx, dy)
        if best is None or move_key > best[0]:
            best = (move_key, [dx, dy])

    if best is None:
        return [0, 0]
    return best[1]
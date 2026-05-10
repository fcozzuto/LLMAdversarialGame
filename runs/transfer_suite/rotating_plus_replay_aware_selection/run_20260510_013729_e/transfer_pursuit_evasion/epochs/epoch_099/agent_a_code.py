def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role") or "").lower()
    act_evader = ("evad" in self_role) or ("run" in self_role) or ("escap" in self_role)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    best = None
    best_key = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                pass
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obs:
                continue
            dist2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            key = (dist2 if not act_evader else -dist2, abs(dx) + abs(dy), dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best = [dx, dy]
    if best is None:
        return [0, 0]
    return best
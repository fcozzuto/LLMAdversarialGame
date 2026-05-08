def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obs = set()
    for o in (observation.get("obstacles", []) or []):
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x = int(o[0]); y = int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = str(observation.get("self_role", "")).lower()
    opponent_role = str(observation.get("opponent_role", "")).lower()
    flee = ("evader" in self_role) or ("evad" in self_role) or ("evasion" in self_role)
    if "pursuer" in self_role or "tag" in self_role:
        flee = False
    if "evader" in opponent_role:
        flee = True
    if "pursuer" in opponent_role:
        flee = False

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    best = None
    best_val = None
    for dx, dy in dirs:
        nx = sx + dx; ny = sy + dy
        if not ok(nx, ny):
            continue
        d = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        val = d if flee else -d
        if best_val is None or val > best_val:
            best_val = val
            best = [dx, dy]

    if best is not None:
        return best

    for dx, dy in dirs:
        nx = sx + dx; ny = sy + dy
        if ok(nx, ny):
            return [dx, dy]
    return [0, 0]
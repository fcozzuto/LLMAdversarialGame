def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in (observation.get("obstacles") or []):
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    def to_set(key):
        s = set()
        for p in (observation.get(key) or []):
            try:
                s.add((int(p[0]), int(p[1])))
            except:
                pass
        return s

    self_t = to_set("self_territory")
    opp_t = to_set("opponent_territory")
    unclaimed = to_set("unclaimed_cells")

    self_cnt = int(observation.get("self_territory_count", len(self_t)) or len(self_t))
    opp_cnt = int(observation.get("opponent_territory_count", len(opp_t)) or len(opp_t))

    # Deterministic tie-break order
    dirs = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    # Choose target
    if self_cnt < opp_cnt and opp_t:
        tx, ty = min(opp_t, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
    else:
        candidates = unclaimed if unclaimed else (observation.get("resources") or [])
        if candidates:
            try:
                tx, ty = min(to_set("unclaimed_cells") if unclaimed else set((int(p[0]), int(p[1])) for p in candidates if len(p) >= 2),
                             key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
            except:
                tx, ty = ox, oy
        else:
            tx, ty = ox, oy

    best = None
    best_d = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
            d = abs(nx - tx) + abs(ny - ty)
            if best_d is None or d < best_d:
                best_d = d
                best = (dx, dy)

    if best is not None:
        return [best[0], best[1]]

    # If all moves blocked, stay deterministic
    if (sx, sy) not in blocked:
        return [0, 0]
    # Otherwise pick a safe move ignoring block (should not happen often)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h:
            return [dx, dy]
    return [0, 0]
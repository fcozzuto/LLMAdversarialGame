def choose_move(observation):
    def get2(k, d=(0, 0)):
        p = observation.get(k, d)
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            return int(p[0]), int(p[1])
        return int(d[0]), int(d[1])

    sx, sy = get2("self_position")
    ox, oy = get2("opponent_position")
    gw = int(observation.get("grid_width", 8) or 8)
    gh = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for it in observation.get("obstacles") or []:
        if isinstance(it, (list, tuple)) and len(it) >= 2:
            x, y = int(it[0]), int(it[1])
            if 0 <= x < gw and 0 <= y < gh:
                obstacles.add((x, y))

    resources = []
    for it in observation.get("resources") or []:
        if isinstance(it, (list, tuple)) and len(it) >= 2:
            x, y = int(it[0]), int(it[1])
            if 0 <= x < gw and 0 <= y < gh and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    self_pos = (sx, sy)
    opp_pos = (ox, oy)

    best = None
    for r in resources:
        ds = manh(self_pos, r)
        do = manh(opp_pos, r)
        # Timing edge: positive means we are closer; contest when opponent is closer.
        edge = do - ds
        # Deterministic tie-break: smaller ds, then lexicographic target.
        score = (edge, -ds, -r[0], -r[1])
        if best is None or score > best[0]:
            best = (score, r)

    target = best[1]
    dx = target[0] - sx
    dy = target[1] - sy
    step_x = 0 if dx == 0 else (1 if dx > 0 else -1)
    step_y = 0 if dy == 0 else (1 if dy > 0 else -1)

    nx, ny = sx + step_x, sy + step_y
    if not (0 <= nx < gw and 0 <= ny < gh) or (nx, ny) in obstacles:
        # Fall back to single-axis deterministic moves
        if 0 <= sx + step_x < gw and (sx + step_x, sy) not in obstacles:
            return [step_x, 0]
        if 0 <= sy + step_y < gh and (sx, sy + step_y) not in obstacles:
            return [0, step_y]
        return [0, 0]
    return [step_x, step_y]
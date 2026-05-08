def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def to_xy(v, default=(0, 0)):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return (int(v[0]), int(v[1]))
        if isinstance(v, dict):
            p = v.get("position", v.get("pos", None))
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                return (int(p[0]), int(p[1]))
        return default

    sx, sy = to_xy(observation.get("self_position", None), (0, 0))
    ox, oy = to_xy(observation.get("opponent_position", None), (sx, sy))

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        x, y = to_xy(o, None)
        if x is None:
            continue
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources", []) or []:
        x, y = to_xy(r, None)
        if x is None:
            continue
        if free(x, y):
            resources.append((x, y))

    if not resources:
        return [0, 0]

    rem = int(observation.get("remaining_resource_count", len(resources)) or len(resources))
    early = rem > 6

    def clamp_step(dx, dy):
        if dx < -1: dx = -1
        if dx > 1: dx = 1
        if dy < -1: dy = -1
        if dy > 1: dy = 1
        return [dx, dy]

    target = None
    best = None
    for tx, ty in resources:
        sd = abs(tx - sx) + abs(ty - sy)
        od = abs(tx - ox) + abs(ty - oy)
        row_bonus = 0
        if early and ty == sy:
            row_bonus = 1  # race resources already on our row
        if (not early) and ty == oy:
            row_bonus = 1  # late game: deny opponent row
        # Prefer cells opponent can't reach much earlier; slight bias to closer resources.
        key = ((od - sd) + row_bonus, -sd)
        if best is None or key > best:
            best = key
            target = (tx, ty)

    tx, ty = target
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # Validate move; if blocked, try best alternative step toward the same target.
    candidates = []
    for mx in (-1, 0, 1):
        for my in (-1, 0, 1):
            if mx == 0 and my == 0:
                pass
            nx, ny = sx + mx, sy + my
            if not free(nx, ny):
                continue
            candidates.append((abs(tx - nx) + abs(ty - ny), abs(ox - nx) + abs(oy - ny), mx, my))
    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: (t[0], -t[1]))
    _, _, mdx, mdy = candidates[0]
    return clamp_step(int(mdx), int(mdy))
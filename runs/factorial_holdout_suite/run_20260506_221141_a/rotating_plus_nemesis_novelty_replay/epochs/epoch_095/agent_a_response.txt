def choose_move(observation):
    def to_xy(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        return 0, 0

    sx, sy = to_xy(observation.get("self_position"))
    ox, oy = to_xy(observation.get("opponent_position"))
    gw = int(observation.get("grid_width", 8) or 8)
    gh = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for it in observation.get("obstacles") or []:
        x, y = to_xy(it)
        if 0 <= x < gw and 0 <= y < gh:
            obstacles.add((x, y))

    resources = []
    for it in observation.get("resources") or []:
        x, y = to_xy(it)
        if 0 <= x < gw and 0 <= y < gh and (x, y) not in obstacles:
            resources.append((x, y))
    if not resources:
        return [0, 0]

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    def step_towards(tx, ty):
        dx = 0
        if tx > sx:
            dx = 1
        elif tx < sx:
            dx = -1
        dy = 0
        if ty > sy:
            dy = 1
        elif ty < sy:
            dy = -1
        return [dx, dy]

    # Opponent greedy target by Manhattan.
    opp_target = min(resources, key=lambda r: (manh(ox, oy, r[0], r[1]), r[0], r[1]))
    tx, ty = opp_target
    opp_d = manh(ox, oy, tx, ty)

    # Score resources by ability to arrive no later than opponent; also value denying near opponent target.
    best_r = resources[0]
    best_key = None
    for r in resources:
        rx, ry = r
        sd = manh(sx, sy, rx, ry)
        od = manh(ox, oy, rx, ry)
        # primary: maximize (od - sd) advantage; secondary: prefer earlier arrival; tertiary: deterministic coords
        deny = (manh(rx, ry, tx, ty) == 0) or (manh(rx, ry, tx, ty) <= 1 and sd <= opp_d + 1)
        key = (-(od - sd), sd, 0 if deny else 1, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = r

    bx, by = best_r
    # Interceptor: if we can beat or strongly pressure opponent's current target, head there.
    my_to_opp = manh(sx, sy, tx, ty)
    if manh(sx, sy, tx, ty) <= opp_d + 0 and (sx, sy) != (tx, ty):
        return step_towards(tx, ty)

    return step_towards(bx, by)
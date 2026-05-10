def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    tr = int(observation.get("turns_remaining", 0))
    remaining = int(observation.get("remaining_resource_count", len(resources)))

    best_score = None
    best_targets = []
    for rx, ry in resources:
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        lead = opd - myd
        secure = 18 if myd <= opd else 0
        time = 3 if myd <= tr else 0
        urgency = 2 if remaining <= 4 else 0
        far_pen = 0.35 * myd if myd > opd else 0
        ts = secure + time + urgency + lead - far_pen
        key = (-ts, myd, rx, ry)
        best_targets.append((key, ts, myd, rx, ry))
    best_targets.sort(key=lambda z: z[0])
    _, _, _, tx, ty = best_targets[0]

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            # Prefer moves that reduce distance to chosen target, and only weakly consider opponent.
            my_next = man(nx, ny, tx, ty)
            opp_next = man(ox, oy, tx, ty)
            # If opponent is also heading there, bias toward still improving our approach.
            score = (my_next, - (opp_next - my_next), abs(dx) + abs(dy))
            candidates.append((score, dx, dy, nx, ny))

    if not candidates:
        return [0, 0]

    candidates.sort(key=lambda z: z[0])
    return [int(candidates[0][1]), int(candidates[0][2])]
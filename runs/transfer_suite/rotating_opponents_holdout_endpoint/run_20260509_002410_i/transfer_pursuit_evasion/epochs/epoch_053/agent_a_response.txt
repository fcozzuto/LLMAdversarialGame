def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or (role == "evader")
    if "pursuer" in role or role == "pursuer":
        is_evader = False
    if "evader" not in role and "pursuer" not in role:
        is_evader = False

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x, y, a, b):
        dx, dy = x - a, y - b
        return dx * dx + dy * dy

    def obs_pen(x, y):
        if (x, y) in obstacles:
            return 10**9
        pen = 0
        for bx, by in obstacles:
            md = abs(x - bx) + abs(y - by)
            if md == 0:
                return 10**9
            if md == 1:
                pen += 6
            elif md == 2:
                pen += 2
        return pen

    best = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)
        pen = obs_pen(nx, ny)
        if pen >= 10**9:
            continue
        score = pen + (d if is_evader else -d)
        if best_score is None:
            best_score, best = score, [dx, dy]
        else:
            if (is_evader and score > best_score) or ((not is_evader) and score < best_score):
                best_score, best = score, [dx, dy]

    if best is None:
        best = [0, 0]
    return best
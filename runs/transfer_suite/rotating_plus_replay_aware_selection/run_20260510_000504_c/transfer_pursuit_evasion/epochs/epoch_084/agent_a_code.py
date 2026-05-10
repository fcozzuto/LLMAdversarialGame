def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ex, ey = int(p[0]), int(p[1])
            if 0 <= ex < w and 0 <= ey < h:
                obstacles.add((ex, ey))

    role = str(observation.get("self_role", "") or "").lower()
    evader = ("evad" in role) or ("escape" in role) or ("runner" in role) or ("flee" in role)

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    best = None
    best_score = -10**30

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        score = 0
        dd_op = d2(nx, ny, ox, oy)
        score += -dd_op if evader else dd_op * 0.8

        if resources:
            mind = 10**18
            for rx, ry in resources:
                v = d2(nx, ny, rx, ry)
                if v < mind:
                    mind = v
            score += (-mind) * 0.6 if mind < 10**18 else 0
        else:
            # small bias to reduce distance to opponent (or increase if evader)
            score += (-dd_op) * 0.05 if evader else (dd_op) * -0.01

        if best is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best
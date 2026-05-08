def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def is_evader(role):
        r = (role or "").lower()
        return ("evader" in r) or ("evasion" in r) or ("avoid" in r)

    self_role = observation.get("self_role", "")
    self_is_evader = is_evader(self_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def count_legal(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                c += 1
        return c

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)

        if self_is_evader:
            primary = -d  # maximize distance
        else:
            primary = d   # minimize distance

        # Prefer moves that "face" the opponent (stable tie-break for wall runner)
        sgnx = 0 if ox == nx else (1 if ox > nx else -1)
        sgny = 0 if oy == ny else (1 if oy > ny else -1)
        align = (dx == sgnx) + (dy == sgny)

        # Secondary: more mobility is generally safer
        mobility = count_legal(nx, ny)

        # Deterministic ordering: include (dx, dy) in tuple to break ties consistently
        if self_is_evader:
            key = (primary, align, mobility, -dx, -dy)
        else:
            key = (-primary, align, mobility, -dx, -dy)

        candidates.append((key, [dx, dy]))

    # If somehow no candidate (shouldn't), stay still
    if not candidates:
        return [0, 0]

    best = None
    for k, m in candidates:
        if best is None or k > best[0]:
            best = (k, m)
    return best[1]
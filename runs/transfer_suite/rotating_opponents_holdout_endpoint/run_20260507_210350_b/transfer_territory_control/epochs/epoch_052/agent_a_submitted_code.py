def choose_move(observation):
    def safe_int(v, d=0):
        try:
            if v is None:
                return d
            if isinstance(v, bool):
                return d
            if isinstance(v, (int,)):
                return int(v)
            if isinstance(v, float):
                return int(v)
            s = str(v).strip()
            if "**" in s or "e" in s.lower():
                return d
            return int(s)
        except:
            return d

    w = safe_int(observation.get("grid_width", 8), 8)
    h = safe_int(observation.get("grid_height", 8), 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = safe_int(sp[0], 0), safe_int(sp[1], 0)
    ox, oy = safe_int(op[0], 0), safe_int(op[1], 0)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = safe_int(p[0], 0), safe_int(p[1], 0)
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, x, y):
        return abs(a - x) + abs(b - y)

    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            candidates.append((dx, dy, nx, ny))

    if not candidates:
        return [0, 0]

    target_list = observation.get("unclaimed_cells") or observation.get("resources") or []
    best_target = None
    best_dist = 10**18
    for p in target_list:
        if p and len(p) >= 2:
            x, y = safe_int(p[0], None), safe_int(p[1], None)
            if x is None or y is None:
                continue
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                d = man(sx, sy, x, y)
                if d < best_dist:
                    best_dist = d
                    best_target = (x, y)

    if best_target is None:
        best_target = (ox, oy)

    best_move = candidates[0][:2]
    best_score = -10**18
    for dx, dy, nx, ny in candidates:
        d = man(nx, ny, best_target[0], best_target[1])
        opp_d = man(nx, ny, ox, oy)
        score = (-d * 10) + (opp_d)
        if dx == 0 and dy == 0:
            score -= 1
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
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

    self_role = observation.get("self_role", "") or ""
    if not is_evader(self_role):
        self_role = observation.get("self_role_name", "") or self_role
    if not is_evader(self_role):
        self_role = observation.get("role", "") or self_role
    evading = is_evader(self_role)

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best_m = (0, 0)
    best_v = None

    def d2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    cur_d = d2(sx, sy, ox, oy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        nd = d2(nx, ny, ox, oy)
        if evading:
            val = nd
        else:
            val = -nd
        # Small tie-break: prefer improving distance direction, then lower max displacement
        improve = nd - cur_d
        if evading:
            tie = -abs(improve)  # higher val dominates; this makes closer-to-max decisions stable
        else:
            tie = -abs(improve)
        val2 = (val, tie, -abs(dx) - abs(dy), dx, dy)
        if best_v is None or val2 > best_v:
            best_v = val2
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]
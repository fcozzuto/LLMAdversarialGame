def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role", "") or "").lower()
    opp_role = str(observation.get("opponent_role", "") or "").lower()
    self_is_pursuer = ("purs" in self_role) or ("purs" in opp_role and "evad" in self_role) or ("pursuer" in self_role)
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def md(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def obs_pen(nx, ny):
        pen = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0: 
                    continue
                if (nx + dx, ny + dy) in obstacles:
                    pen += 2
        return pen

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist = md(nx, ny, ox, oy)
        # Deterministic tie-break: prefer lower dx, then lower dy, via tuple ordering.
        if self_is_pursuer:
            score = -dist * 10 - obs_pen(nx, ny)
        else:
            # Flee to maximize distance; also bias toward a corner opposite the pursuer.
            corner = (w - 1, h - 1) if (ox < w // 2 and oy < h // 2) else (0 if ox >= w // 2 else w - 1, 0 if oy >= h // 2 else h - 1)
            corner_benefit = md(nx, ny, corner[0], corner[1]) - md(sx, sy, corner[0], corner[1])
            score = dist * 10 + corner_benefit * 3 - obs_pen(nx, ny)
        candidates.append((score, dx, dy))
    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: (-(t[0]), t[1], t[2]))
    return [candidates[0][1], candidates[0][2]]
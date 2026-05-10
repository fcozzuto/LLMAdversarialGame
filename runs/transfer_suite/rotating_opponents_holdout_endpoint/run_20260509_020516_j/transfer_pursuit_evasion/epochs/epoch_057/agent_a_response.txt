def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])
    role = observation.get("self_role") or "pursuer"

    obstacles = set()
    for it in observation.get("obstacles") or []:
        try:
            if isinstance(it, dict):
                x, y = it.get("x"), it.get("y")
            else:
                x, y = it[0], it[1]
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    moves.sort()
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    scored = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
        d = dist2(nx, ny, ox, oy)
        if role.lower() == "evader":
            score = d  # maximize distance
            # if near walls/obstacles, slightly prefer staying with more escape room
            if nx in (0, w - 1) or ny in (0, h - 1):
                score -= 1
        else:
            score = -d  # minimize distance
            if nx in (0, w - 1) or ny in (0, h - 1):
                score -= 0.2
        scored.append((score, (dx, dy), (nx, ny)))

    scored.sort(key=lambda t: (t[0], t[2][0], t[2][1], t[1][0], t[1][1]), reverse=True)
    return [int(scored[0][1][0]), int(scored[0][1][1])]
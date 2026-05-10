def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])
    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))
    role = observation.get("self_role") or ""
    mv = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def dist2(x, y, a, b):
        dx = x - a
        dy = y - b
        return dx * dx + dy * dy

    # Fallback: if roles unknown, play evasion-ish to avoid capture pressure
    pursuer = str(role).lower().find("purs") >= 0
    # If evader/pursuer strings are absent or inconsistent:
    if str(role).lower() in ("", "evader"):
        pursuer = False

    best = None  # (score, stepsBlocked, nx, ny)
    for dx, dy in mv:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)

        # Additional local obstacle pressure: prefer moves that have more options next turn
        free = 0
        for ddx, ddy in mv:
            tx, ty = nx + ddx, ny + ddy
            if inb(tx, ty):
                free += 1

        if pursuer:
            # Minimize distance; break ties by maximizing freedom
            score = -d
            tie = (-free, nx, ny)
        else:
            # Maximize distance; break ties by maximizing freedom
            score = d
            tie = (-free, -nx, -ny)

        cand = (score, tie, nx, ny)
        if best is None or cand[0] > best[0] or (cand[0] == best[0] and cand[1] < best[1]):
            best = cand

    if best is None:
        return [0, 0]
    _, _, nx, ny = best
    return [nx - sx, ny - sy]
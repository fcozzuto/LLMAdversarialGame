def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    obstacles = observation.get("obstacles", []) or []
    blocked = {(p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def passable(x, y):
        return inb(x, y) and (x, y) not in blocked

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def get_scores():
        s = observation.get("scores", {}) or {}
        if isinstance(s, dict):
            a = s.get("self", s.get("me", s.get("player", 0)))
            b = s.get("opponent", s.get("op", s.get("enemy", 0)))
            return a if isinstance(a, (int, float)) else 0, b if isinstance(b, (int, float)) else 0
        return 0, 0

    self_score, opp_score = get_scores()
    role = (observation.get("self_role") or "").lower()
    evader = ("evad" in role) or ("runner" in role) or ("escape" in role) or (self_score >= opp_score)
    resources = observation.get("resources", []) or []
    res = [(p[0], p[1]) for p in resources if isinstance(p, (list, tuple)) and len(p) >= 2]

    best = None
    best_sc = None
    if res:
        tx, ty = min(res, key=lambda p: man(sx, sy, p[0], p[1]))
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not passable(nx, ny):
                continue
            dres = man(nx, ny, tx, ty)
            dob = man(nx, ny, ox, oy)
            sc = (dres - 2 * dob) if not evader else (-dres + dob)
            if best_sc is None or sc < best_sc:
                best_sc = sc
                best = (dx, dy)
    else:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not passable(nx, ny):
                continue
            dob = man(nx, ny, ox, oy)
            sc = (-dob if evader else dob)
            if best_sc is None or sc < best_sc:
                best_sc = sc
                best = (dx, dy)

    if best is None:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if passable(nx, ny):
                return [dx, dy]
        return [0, 0]
    return [int(best[0]), int(best[1])]
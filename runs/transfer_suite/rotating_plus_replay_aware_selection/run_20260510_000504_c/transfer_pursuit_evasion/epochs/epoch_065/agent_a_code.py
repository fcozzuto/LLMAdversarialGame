def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", None) or [0, 0]
    ox, oy = observation.get("opponent_position", None) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_role = str(observation.get("self_role", "") or "").lower()
    opponent_role = str(observation.get("opponent_role", "") or "").lower()
    evader = ("evad" in self_role) or ("escape" in self_role) or ("runner" in self_role) or ("purs" in opponent_role)

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, dict):
            x = r.get("x", r.get("pos", [None, None])[0] if isinstance(r.get("pos"), (list, tuple)) else None)
            y = r.get("y", r.get("pos", [None, None])[1] if isinstance(r.get("pos"), (list, tuple)) else None)
            if x is not None and y is not None:
                res.append((int(x), int(y)))
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            res.append((int(r[0]), int(r[1])))
    if not res and (observation.get("remaining_resource_count", 0) or 0) > 0:
        res = []

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        d_opp = dist(nx, ny, ox, oy)
        score = (d_opp if evader else -d_opp)

        if res:
            d_res = 10**9
            for rx, ry in res:
                d = dist(nx, ny, rx, ry)
                if d < d_res: d_res = d
            score += (-d_res if not evader else -d_res * 0.7)

        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]
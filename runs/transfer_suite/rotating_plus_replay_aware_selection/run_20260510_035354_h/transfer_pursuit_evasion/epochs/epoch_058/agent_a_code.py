def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                res.append((x, y))

    r = (observation.get("self_role", "") or "").lower()
    pursuer = ("purs" in r) or ("chaser" in r) or ("hunter" in r) or ("catcher" in r)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    best = None
    best_score = None
    dpos = dist2(sx, sy, ox, oy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue
        dopp = dist2(nx, ny, ox, oy)
        center = dist2(nx, ny, cx, cy)

        if res:
            rr = min(dist2(nx, ny, px, py) for px, py in res)
        else:
            rr = 0

        # pursuer: minimize distance to opponent; evader: maximize distance
        score = (dopp if not pursuer else -dopp)
        # prefer resources slightly when available
        score += (-rr * 0.02 if not pursuer else -rr * 0.01)
        # center tie-break
        score += -center * 1e-6

        if best_score is None or (score > best_score) or (score == best_score and (dopp < dpos) == pursuer):
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best
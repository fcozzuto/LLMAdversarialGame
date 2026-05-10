def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    resources = []
    for p in (observation.get("resources", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resources.append((int(p[0]), int(p[1])))

    targets = resources or []
    if not targets:
        for p in (observation.get("unclaimed_cells", []) or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                targets.append((int(p[0]), int(p[1])))
    if not targets:
        opp_terr = []
        for p in (observation.get("opponent_territory", []) or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                opp_terr.append((int(p[0]), int(p[1])))
        targets = opp_terr

    if not targets:
        targets = [(w // 2, h // 2)]

    cx, cy = w // 2, h // 2
    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    best = None
    best_score = None
    cand = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        if (nx, ny) == (ox, oy):
            continue
        t = min(targets, key=lambda p: dist2(nx, ny, p[0], p[1]))
        score = dist2(nx, ny, t[0], t[1])
        score += 0.1 * dist2(nx, ny, cx, cy)
        score -= 0.01 * dist2(nx, ny, ox, oy)
        if best_score is None or score < best_score:
            best_score = score
            best = [dx, dy]

    if best is not None:
        return best
    return [0, 0]
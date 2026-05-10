def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role") or "").lower()
    i_iam_pursuer = ("pursuer" in role) or ("pursue" in role) or ("chaser" in role) or ("pursuit" in role)

    deltas = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obs
    def dist(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    def obs_risk(x, y):
        risk = 0
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            if (x + dx, y + dy) in obs: risk += 2
        return risk

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    best_dx, best_dy = 0, 0

    if i_iam_pursuer:
        best_score = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): continue
            # Higher score = closer to evader, safer from obstacles
            sc = -dist(nx, ny, ox, oy) - 0.3 * obs_risk(nx, ny)
            if sc > best_score or (sc == best_score and (dx, dy) < (best_dx, best_dy)):
                best_score, best_dx, best_dy = sc, dx, dy
    else:
        # Evader: maximize distance and prefer corners; avoid getting near obstacles
        px_tgt = None
        best_corner_val = -10**18
        for cx, cy in corners:
            val = dist(cx, cy, ox, oy) - 0.5 * obs_risk(cx, cy) - 0.1 * (abs(cx - sx) + abs(cy - sy))
            if val > best_corner_val:
                best_corner_val, px_tgt = val, (cx, cy)

        tx, ty = px_tgt
        best_score = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): continue
            # Higher score = farther from pursuer, closer to target corner, low risk
            sc = dist(nx, ny, ox, oy) + 0.35 * dist(nx, ny, tx, ty) * (-0.5) - 0.3 * obs_risk(nx, ny)
            if sc > best_score or (sc == best_score and (dx, dy) < (best_dx, best_dy)):
                best_score, best_dx, best_dy = sc, dx, dy

    return [int(best_dx), int(best_dy)]
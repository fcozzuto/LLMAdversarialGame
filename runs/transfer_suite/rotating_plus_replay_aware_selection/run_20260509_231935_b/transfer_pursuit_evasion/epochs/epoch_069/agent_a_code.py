def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    i_am_pursuer = ("pursuer" in self_role) or (("evader" not in self_role) and ("pursuer" not in opp_role))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    if not i_am_pursuer:
        best = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            score = dist2(nx, ny, ox, oy)
            if best is None or score > best[0] or (score == best[0] and (nx, ny) < best[1]):
                best = (score, (nx, ny))
        if best is None:
            return [0, 0]
        nx, ny = best[1]
        return [nx - sx, ny - sy]

    # pursuer: minimize distance to opponent, but also bias toward blocking the likely corner.
    target_corner = min(corners, key=lambda c: dist2(ox, oy, c[0], c[1]))

    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d_op = dist2(nx, ny, ox, oy)
        d_corner = dist2(nx, ny, target_corner[0], target_corner[1])
        # primary: chase; secondary: occupy/approach the corner choke point.
        score = d_op * 1000 + d_corner
        if best is None or score < best[0] or (score == best[0] and (nx, ny) < best[1]):
            best = (score, (nx, ny))

    if best is None:
        return [0, 0]
    nx, ny = best[1]
    return [nx - sx, ny - sy]
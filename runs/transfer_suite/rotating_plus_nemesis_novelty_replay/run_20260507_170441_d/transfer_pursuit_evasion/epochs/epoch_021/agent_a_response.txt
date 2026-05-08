def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for o in (observation.get("obstacles", []) or []):
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    role = str(observation.get("self_role", "")).lower()
    is_pursuer = ("purs" in role) or ("tag" in role) or ("hunter" in role)

    # Estimate evader's likely target corner: farthest corner from us
    best_corner = corners[0]
    best_cd = -1
    for cx, cy in corners:
        cd = dist2(sx, sy, cx, cy)
        if cd > best_cd:
            best_cd = cd
            best_corner = (cx, cy)
    tcx, tcy = best_corner

    best_move = [0, 0]
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        d_opp = dist2(nx, ny, ox, oy)
        d_tc = dist2(nx, ny, tcx, tcy)
        d_corner_op = max(dist2(nx, ny, cx, cy) for cx, cy in corners)

        if is_pursuer:
            # Tighten on opponent while progressing to (estimated) evader target corner
            score = (-d_opp) + 0.08 * (-d_tc) + 0.02 * (-d_corner_op)
        else:
            # Get away from pursuer while tending to corners
            score = (d_opp) + 0.12 * (d_tc) + 0.04 * (d_corner_op)

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]
def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
    cap_r = int(observation.get("capture_radius", 0) or 0)
    cap2 = cap_r * cap_r

    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    resources = observation.get("resources", []) or []
    targets = []
    for r in resources:
        if r is not None and len(r) >= 2:
            targets.append((int(r[0]), int(r[1])))

    best_target = None
    if targets:
        best_target = min(targets, key=lambda t: dist2((sx, sy), t))

    def can_capture(pos_from, pos_to):
        return cap_r == 0 and pos_from == pos_to or dist2(pos_from, pos_to) <= cap2

    # If we can capture immediately, do it.
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny) and can_capture((nx, ny), (ox, oy)):
            return [dx, dy]

    best = None
    best_tuple = None  # (risk, -dist_to_opp, dist_to_target, dx, dy)
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        risk = 0
        # Risk: can opponent capture us after its move?
        for odx, ody in cand:
            mx, my = ox + odx, oy + ody
            if valid(mx, my) and can_capture((mx, my), (nx, ny)):
                risk = 1
                break
        distopp = dist2((nx, ny), (ox, oy))
        disttar = dist2((nx, ny), best_target) if best_target else 0
        tup = (risk, -distopp, disttar, dx, dy)
        if best_tuple is None or tup < best_tuple:
            best_tuple = tup
            best = (dx, dy)

    if best is None:
        for dx, dy in cand:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]
    return [best[0], best[1]]
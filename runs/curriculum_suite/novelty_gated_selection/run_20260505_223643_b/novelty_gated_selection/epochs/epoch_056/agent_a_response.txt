def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def norm_point(p):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            return int(p[0]), int(p[1])
        if isinstance(p, dict):
            if "position" in p and p["position"]:
                q = p["position"]
                return int(q[0]), int(q[1])
            if "x" in p and "y" in p:
                return int(p["x"]), int(p["y"])
        return None

    obstacles = set()
    for item in observation.get("obstacles", []) or []:
        q = norm_point(item)
        if q:
            x, y = q
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for item in observation.get("resources", []) or []:
        q = norm_point(item)
        if q:
            x, y = q
            if 0 <= x < w and 0 <= y < h:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Intercept the resource the opponent is currently closest to.
    target = min(resources, key=lambda r: man((ox, oy), r))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    opp_d = man((ox, oy), target)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d = man((nx, ny), target)
        # Prefer moves that give us the edge on the contested target.
        edge = 2 if d <= opp_d else 0
        # Slightly prefer positions that also move toward any resource if interception is weak.
        alt = min((man((nx, ny), r) for r in resources), default=10**9)
        # Keep determinism with tie-break using opponent distance and coordinates.
        key = (d - edge, alt, man((nx, ny), (ox, oy)), nx, ny, dx, dy)
        if best is None or key < best[0]:
            best = (key, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]
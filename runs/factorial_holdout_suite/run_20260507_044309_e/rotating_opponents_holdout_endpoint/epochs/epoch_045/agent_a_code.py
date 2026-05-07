def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [7, 7])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources_in = observation.get("resources", []) or []
    obstacles_in = observation.get("obstacles", []) or []

    obstacles = set()
    for p in obstacles_in:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in resources_in:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resources.append((int(p[0]), int(p[1])))
    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Target: first try to secure resources where we are (likely) closer; if none, pick best relative lead.
    best = None
    best_key = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Prefer positive lead (we closer), otherwise minimize how bad it is.
        # Secondary: favor closer overall so we act sooner.
        lead = od - sd
        key = (lead > 0, lead, -sd, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1),
             (1, 1), (1, -1), (-1, 1), (-1, -1)]

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Move choice: minimize our distance to target; if tie, maximize opponent distance from that target.
        nd = man(nx, ny, tx, ty)
        od_to = man(ox, oy, tx, ty)
        opp_push = man(ox, oy, tx, ty) - man(ox, oy, nx, ny)
        score = ( -nd, -(od_to), opp_push, -dx, -dy )
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
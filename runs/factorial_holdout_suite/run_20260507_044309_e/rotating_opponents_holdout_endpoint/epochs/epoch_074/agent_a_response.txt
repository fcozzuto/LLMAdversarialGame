def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Choose a resource we can reach first (or, if none, the least contested).
    best = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Primary: we prefer ds<=do; encoded as margin (do-ds). Secondary: smaller ds; tertiary: stable coord.
        key = (do - ds, -ds, -abs(rx - sx) - abs(ry - sy), rx, ry)
        if best is None or key > best_key:
            best = (rx, ry)
            best_key = key

    rx, ry = best
    if sx == rx and sy == ry:
        return [0, 0]

    candidates = []
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d1 = cheb(nx, ny, rx, ry)
        d2 = cheb(nx, ny, ox, oy)  # mild prefer safety
        # Also discourage moves that would make the target too easy for opponent next step.
        opp_to_target = cheb(ox, oy, rx, ry)
        score = (-(d1), (opp_to_target - cheb(ox, oy, rx, ry) - 0), -d2, dx, dy)
        candidates.append((score, dx, dy))
    if not candidates:
        return [0, 0]

    candidates.sort(reverse=True)
    return [int(candidates[0][1]), int(candidates[0][2])]
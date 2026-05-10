def choose_move(observation):
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        x = y = None
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
        elif isinstance(p, dict):
            if "position" in p and isinstance(p["position"], (list, tuple)) and len(p["position"]) >= 2:
                x, y = int(p["position"][0]), int(p["position"][1])
            elif "x" in p and "y" in p:
                x, y = int(p["x"]), int(p["y"])
        if x is not None and y is not None:
            obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        x = y = None
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
        elif isinstance(r, dict):
            if "position" in r and isinstance(r["position"], (list, tuple)) and len(r["position"]) >= 2:
                x, y = int(r["position"][0]), int(r["position"][1])
            elif "x" in r and "y" in r:
                x, y = int(r["x"]), int(r["y"])
        if x is not None and y is not None:
            resources.append((x, y))

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = None
    best_score = -10**18

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        if resources:
            dmin = 10**9
            for rx, ry in resources:
                d = abs(nx - rx) + abs(ny - ry)
                if d < dmin:
                    dmin = d
            score = -dmin
        else:
            score = 0
        score += -0.1 * (abs(nx - ox) + abs(ny - oy))
        if best is None or score > best_score:
            best, best_score = [dx, dy], score

    if best is None:
        return [0, 0]
    return best
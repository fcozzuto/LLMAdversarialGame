def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [0, 0])[:2]

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            if "position" in r and isinstance(r["position"], (list, tuple)) and len(r["position"]) >= 2:
                resources.append((int(r["position"][0]), int(r["position"][1])))
            elif "x" in r and "y" in r:
                resources.append((int(r["x"]), int(r["y"])))
    if resources:
        resources = [p for p in resources if p not in obstacles]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    tx, ty = (w // 2, h // 2)
    if resources:
        best = None
        for rx, ry in resources:
            myd = md(sx, sy, rx, ry)
            opd = md(ox, oy, rx, ry)
            lead = myd - opd  # smaller => better relative
            score = lead * 1000 + myd  # tie-break by getting closer
            if best is None or score < best[0]:
                best = (score, rx, ry)
        tx, ty = best[1], best[2]

    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        my_to_target = md(nx, ny, tx, ty)
        opp_to_target = md(ox, oy, tx, ty)
        rel = my_to_target - opp_to_target
        # If closer than opponent, strongly prefer; else still reduce own distance.
        val = rel * 1000 + my_to_target
        # Slightly prefer moves that increase distance from opponent when not leading (denier handling).
        val += (0 if rel <= 0 else -0.01 * md(nx, ny, ox, oy))
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    if isinstance(dx, int) and isinstance(dy, int) and dx in (-1, 0, 1) and dy in (-1, 0, 1):
        return [dx, dy]
    return [0, 0]
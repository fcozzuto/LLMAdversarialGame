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
    resources = [p for p in resources if p not in obstacles]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = w // 2, h // 2
    else:
        # Pick resource where we have maximal distance advantage; if tied, pick nearest to us.
        best = None
        for rx, ry in resources:
            myd = md(sx, sy, rx, ry)
            opd = md(ox, oy, rx, ry)
            midline_bias = (w // 2 - rx) * (1 if sx <= w // 2 else -1)  # deterministic bias to our half
            score = (opd - myd, midline_bias, -myd)
            if best is None or score > best[0]:
                best = (score, rx, ry)
        tx, ty = best[1], best[2]

    best_move = [0, 0]
    best_val = None
    # Evaluate immediate move utility toward chosen target; avoid obstacles deterministically.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dcur = md(nx, ny, tx, ty)
        myd_now = md(sx, sy, tx, ty)
        opd_now = md(ox, oy, tx, ty)
        # Encourage getting closer and contesting (myd_now vs opd_now); slight tie-break by preferring forward progress.
        forward = (dy, dx)
        val = (-dcur, -(dcur - myd_now), (opd_now - dcur), forward, -((nx == sx and ny == sy)))
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move if best_val is not None else [0, 0]
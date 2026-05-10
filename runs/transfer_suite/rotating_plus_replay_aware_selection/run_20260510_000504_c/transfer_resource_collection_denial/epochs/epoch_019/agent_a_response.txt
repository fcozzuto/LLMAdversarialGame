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
            rx, ry = int(r[0]), int(r[1])
        elif isinstance(r, dict):
            if "position" in r and isinstance(r["position"], (list, tuple)) and len(r["position"]) >= 2:
                rx, ry = int(r["position"][0]), int(r["position"][1])
            elif "x" in r and "y" in r:
                rx, ry = int(r["x"]), int(r["y"])
            else:
                continue
        else:
            continue
        if (rx, ry) not in obstacles and 0 <= rx < w and 0 <= ry < h:
            resources.append((rx, ry))

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def score_target(tx, ty):
        myd = md(sx, sy, tx, ty)
        opd = md(ox, oy, tx, ty)
        # Primary: maximize my advantage (opd - myd). Secondary: smaller myd.
        return (opd - myd) * 1000 - myd

    if resources:
        best_tx, best_ty = resources[0]
        best_sc = score_target(best_tx, best_ty)
        for tx, ty in resources[1:]:
            sc = score_target(tx, ty)
            if sc > best_sc:
                best_sc = sc
                best_tx, best_ty = tx, ty
    else:
        best_tx, best_ty = w // 2, h // 2

    dx = 0
    dy = 0
    if best_tx > sx:
        dx = 1
    elif best_tx < sx:
        dx = -1
    if best_ty > sy:
        dy = 1
    elif best_ty < sy:
        dy = -1

    # Avoid obvious obstacle if possible by dropping one component.
    nx, ny = sx + dx, sy + dy
    if (dx != 0 or dy != 0) and (nx, ny) in obstacles:
        options = []
        if dx != 0:
            options.append((dx, 0))
        if dy != 0:
            options.append((0, dy))
        if dx != 0 and dy != 0:
            options.append((dx, dy))  # in case obstacle not actually blocking next
        # Deterministic choose best option by resulting md to target.
        best = None
        bestd = None
        for odx, ody in options:
            tx, ty = sx + odx, sy + ody
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) not in obstacles:
                d = md(tx, ty, best_tx, best_ty)
                if best is None or d < bestd:
                    bestd = d
                    best = (odx, ody)
        if best is not None:
            dx, dy = best

    return [int(dx), int(dy)]
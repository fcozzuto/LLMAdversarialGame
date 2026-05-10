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

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(ax, ay, bx, by): return max(abs(ax - bx), abs(ay - by))
    def score_goal(tx, ty):
        myd = cheb(sx, sy, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # prioritize immediate advantage; break ties toward closer-to-us
        return (opd - myd, -myd, -tx, -ty)

    if resources:
        best = None
        for tx, ty in resources:
            sc = score_goal(tx, ty)
            if best is None or sc > best[0]:
                best = (sc, tx, ty)
        tx, ty = best[1], best[2]
    else:
        # fallback: drift toward the side that can collect earlier relative to opponent
        tx = 0 if sx > ox else w - 1
        ty = h // 2
        # if target is blocked, stay near current y
        if (tx, ty) in obstacles:
            ty = max(0, min(h - 1, sy + (1 if ty > sy else (-1 if ty < sy else 0))))
        if (tx, ty) in obstacles: tx, ty = sx, sy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # minimize distance to chosen target; add small bias away from opponent to secure contested resources
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(nx, ny, ox, oy)
        # deterministic tie-breakers
        cand = (-(myd), (opd), -abs(nx - tx), -abs(ny - ty), dx, dy)
        if bestm is None or cand > bestm[0]:
            bestm = (cand, dx, dy)

    if bestm is None:
        return [0, 0]
    return [bestm[1], bestm[2]]
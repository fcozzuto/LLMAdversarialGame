def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [0, 0])[:2]
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
    res = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            if "position" in r and isinstance(r["position"], (list, tuple)) and len(r["position"]) >= 2:
                res.append((int(r["position"][0]), int(r["position"][1])))
            elif "x" in r and "y" in r:
                res.append((int(r["x"]), int(r["y"])))
    res = [p for p in res if p not in obstacles]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def md(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not res:
        # No visible resources: drift to reduce distance to opponent's corner-side resources if any
        tx, ty = (0, h - 1) if (sx + sy) > (ox + oy) else (w - 1, 0)
        best = (10**9, 0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            score = md(nx, ny, tx, ty) + 0.15 * md(nx, ny, ox, oy)
            t = (score, md(nx, ny, tx, ty), dx, dy)
            if t < best:
                best = (t[0], t[2], t[3])
        return [best[1], best[2]]

    best_target = None
    best_key = None
    for (rx, ry) in res:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        # Prefer resources where we are earlier; otherwise contest by minimizing opponent lead.
        lead = od - sd
        key = (-(lead), sd, od, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target
    best_move = (10**9, 0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        self_to = md(nx, ny, tx, ty)
        opp_to = md(nx, ny, ox, oy)
        # If opponent is close to the target, prioritize immediate capture race.
        race = 0
        if md(ox, oy, tx, ty) <= md(sx, sy, tx, ty):
            race = 0.25
        score = self_to + 0.12 * opp_to + race * self_to
        t = (score, self_to, dx, dy)
        if t < best_move:
            best_move = t
    return [best_move[2], best_move[3]]
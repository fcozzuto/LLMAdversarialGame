def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    res = {}
    for r in (observation.get("resources") or []):
        if isinstance(r, dict):
            px, py = r.get("position", (None, None))
            if px is None:
                px, py = r.get("x"), r.get("y")
            if px is None or py is None:
                continue
            px, py = int(px), int(py)
            val = r.get("value", 1)
            try:
                val = float(val)
            except:
                val = 1.0
            res[(px, py)] = val
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            px, py = int(r[0]), int(r[1])
            val = r[2] if len(r) >= 3 else 1
            try:
                val = float(val)
            except:
                val = 1.0
            res[(px, py)] = val

    dirs = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        sc = 0.0
        sc += res.get((nx, ny), 0.0) * 1000.0
        if res:
            # Move toward nearest resource (approx via min manhattan)
            md = 10**9
            for (rx, ry) in res.keys():
                d = abs(rx - nx) + abs(ry - ny)
                if d < md:
                    md = d
            sc += (200.0 / (md + 1))
        # Avoid getting close to opponent
        dpo = abs(ox - nx) + abs(oy - ny)
        sc += dpo * 1.5
        if best is None or sc > best_score:
            best_score = sc
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best
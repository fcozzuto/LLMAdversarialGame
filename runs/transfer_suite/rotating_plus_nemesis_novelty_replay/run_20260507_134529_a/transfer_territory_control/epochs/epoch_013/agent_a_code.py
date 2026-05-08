def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        out = set()
        pts = observation.get(key) or []
        for p in pts:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    out.add((x, y))
        return out

    obstacles = to_set("obstacles")
    resources = to_set("resources")
    unclaimed = to_set("unclaimed_cells")
    our = to_set("self_territory")
    opp = to_set("opponent_territory")

    if not resources and unclaimed:
        resources = unclaimed

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = None
    best_score = -10**18

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Choose a target: nearest resource if any; otherwise nearest border cell not in obstacles.
    if resources:
        tx, ty = min(resources, key=lambda p: man(sx, sy, p[0], p[1]))
    else:
        # Prefer cells closer to center deterministically
        cx, cy = (w - 1) // 2, (h - 1) // 2
        tx, ty = cx, cy

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        d_t = man(nx, ny, tx, ty)
        d_o = man(nx, ny, ox, oy)
        on_res = 1 if (nx, ny) in resources else 0
        on_our = 1 if (nx, ny) in our else 0
        on_opp = 1 if (nx, ny) in opp else 0

        # Deterministic heuristic: seek resources/our territory; avoid getting too close to opponent; also reduce distance to target.
        score = (on_res * 1000) + (on_our * 50) - (on_opp * 200) + (d_o * 2) - d_t
        if score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]
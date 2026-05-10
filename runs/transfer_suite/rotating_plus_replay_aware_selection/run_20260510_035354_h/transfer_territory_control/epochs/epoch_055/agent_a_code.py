def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    ax, ay = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs
    targets = []
    for k in ("unclaimed_cells", "resources"):
        v = observation.get(k)
        if isinstance(v, (list, tuple)) and v:
            for p in v:
                if isinstance(p, (list, tuple)) and len(p) >= 2:
                    targets.append((p[0], p[1]))
            if targets:
                break
    if not targets:
        opp_terr = observation.get("opponent_territory") or []
        for p in opp_terr:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                targets.append((p[0], p[1]))
        if not targets:
            targets = [(ox, oy)]
    def mdist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)
    tx, ty = min(targets, key=lambda t: mdist(ax, ay, t[0], t[1]))
    best = None
    best_val = None
    for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0), (0, 0)):
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny):
            continue
        # Prefer approaching target; lightly penalize moving toward opponent
        val = mdist(nx, ny, tx, ty) - 0.15 * mdist(nx, ny, ox, oy)
        if best is None or val < best_val:
            best = (dx, dy)
            best_val = val
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]
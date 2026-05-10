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
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy))

    if not legal:
        return [0, 0]
    if not resources:
        return sorted(legal)[0]

    best_move = (0, 0)
    best_val = None

    for dx, dy in sorted(legal):
        nx, ny = sx + dx, sy + dy
        # Prefer cells that maximize advantage over opponent on reachable resources.
        val = -10**9
        for rx, ry in resources:
            d_self = md(nx, ny, rx, ry)
            d_opp = md(ox, oy, rx, ry)
            # Advantage: take resources before opponent; tie-break towards closeness.
            cand = (d_opp - d_self) * 100 - d_self
            if cand > val:
                val = cand
        # Small secondary tie-break: closer to nearest resource.
        nearest = min(md(nx, ny, rx, ry) for (rx, ry) in resources)
        val2 = (val, -nearest)
        if best_val is None or val2 > best_val:
            best_val = val2
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
        elif isinstance(p, dict):
            if "position" in p and isinstance(p["position"], (list, tuple)) and len(p["position"]) >= 2:
                obstacles.add((int(p["position"][0]), int(p["position"][1])))
            elif "x" in p and "y" in p:
                obstacles.add((int(p["x"]), int(p["y"])))

    resources = []
    for r in (observation.get("resources", []) or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            if "position" in r and isinstance(r["position"], (list, tuple)) and len(r["position"]) >= 2:
                resources.append((int(r["position"][0]), int(r["position"][1])))
            elif "x" in r and "y" in r:
                resources.append((int(r["x"]), int(r["y"])))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        best = (0, 0)
        bestd = -1
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = abs(nx - ox) + abs(ny - oy)
            if d > bestd or (d == bestd and (dx, dy) < best):
                bestd, best = d, (dx, dy)
        return [best[0], best[1]]

    resources = [(x, y) for (x, y) in resources if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles]
    if not resources:
        return [0, 0]

    best = (0, 0)
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = 10**9
        for rx, ry in resources:
            d = abs(nx - rx) + abs(ny - ry)
            if d < nd:
                nd = d
        # prefer closer to resources; tie-break away from opponent, then deterministic order
        v = (-nd, -(abs(nx - ox) + abs(ny - oy)), dx, dy)
        if bestv is None or v > bestv:
            bestv, best = v, (dx, dy)
    return [best[0], best[1]]
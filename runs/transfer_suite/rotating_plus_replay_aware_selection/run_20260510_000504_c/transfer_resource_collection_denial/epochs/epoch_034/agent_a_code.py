def choose_move(observation):
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

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

    if not resources:
        return [0, 0]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best_target = resources[0]
    best_key = (-10**9, 10**9, 10**9)
    for t in resources:
        ds = md((sx, sy), t)
        do = md((ox, oy), t)
        lead = do - ds  # positive means we are closer
        key = (lead, -ds, -(t[0] * 100 + t[1]))
        if key > best_key:
            best_key = key
            best_target = t

    tx, ty = best_target

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    cur = (sx, sy)
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        ns = md((nx, ny), (tx, ty))
        no = md((ox, oy), (tx, ty))
        race = no - ns
        tie = -abs(nx - tx) - abs(ny - ty)
        candidates.append(((race, tie, -ns, dx, dy), (dx, dy)))

    if not candidates:
        # fallback: allow obstacle move (engine keeps in place anyway)
        dx, dy = (0 if sx == tx else (1 if tx > sx else -1)), (0 if sy == ty else (1 if ty > sy else -1))
        if (sx + dx, sy + dy) in obstacles:
            return [0, 0]
        return [dx, dy]

    candidates.sort(reverse=True)
    return [int(candidates[0][1][0]), int(candidates[0][1][1])]
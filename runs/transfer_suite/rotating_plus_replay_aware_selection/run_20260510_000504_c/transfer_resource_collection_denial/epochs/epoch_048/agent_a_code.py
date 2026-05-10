def choose_move(observation):
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    width = int(observation.get("grid_width") or 8)
    height = int(observation.get("grid_height") or 8)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
        elif isinstance(p, dict):
            if "position" in p and isinstance(p["position"], (list, tuple)) and len(p["position"]) >= 2:
                obstacles.add((int(p["position"][0]), int(p["position"][1])))
            elif "x" in p and "y" in p:
                obstacles.add((int(p["x"]), int(p["y"])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            if "position" in r and isinstance(r["position"], (list, tuple)) and len(r["position"]) >= 2:
                resources.append((int(r["position"][0]), int(r["position"][1])))
            elif "x" in r and "y" in r:
                resources.append((int(r["x"]), int(r["y"])))

    if not resources:
        return [0, 0]

    def inside(x, y):
        return 0 <= x < width and 0 <= y < height

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Resource choice: beat opponent, but if opponent is closer to everything, deny by choosing a "least-worse" target.
    best = None
    best_key = None
    for rx, ry in resources:
        dS = dist((sx, sy), (rx, ry))
        dO = dist((ox, oy), (rx, ry))
        score = (dO - dS, -dS)  # larger is better: opponent further than us; then closer to us
        key = (score[0], score[1], -rx, -ry)  # deterministic tie-break
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    desired_dx = 0 if tx == sx else (1 if tx > sx else -1)
    desired_dy = 0 if ty == sy else (1 if ty > sy else -1)
    moves = [
        (desired_dx, desired_dy),
        (desired_dx, 0),
        (0, desired_dy),
        (desired_dx, -desired_dy),
        (-desired_dx, desired_dy),
        (-desired_dx, 0),
        (0, -desired_dy),
        (-desired_dx, -desired_dy),
        (0, 0),
    ]

    # Order by resulting manhattan distance to target, then deterministic preference list index
    scored = []
    for i, (dx, dy) in enumerate(moves):
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        scored.append((abs(nx - tx) + abs(ny - ty), i, dx, dy))
    if not scored:
        return [0, 0]
    scored.sort()
    return [int(scored[0][2]), int(scored[0][3])]
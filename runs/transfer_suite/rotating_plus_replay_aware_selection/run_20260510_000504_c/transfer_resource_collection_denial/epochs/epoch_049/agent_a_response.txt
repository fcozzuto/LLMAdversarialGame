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

    # Pick a resource where we are not clearly behind; tie-break by deterministic score.
    best = None
    for rx, ry in resources:
        dS = dist((sx, sy), (rx, ry))
        dO = dist((ox, oy), (rx, ry))
        lead = dO - dS  # positive means we are closer
        # Prefer winning races; then lower self distance; then deterministic coordinate order.
        cand = (-(lead > 0), -lead, dS, rx, ry)
        if best is None or cand < best[0]:
            best = (cand, (rx, ry))
    _, target = best
    tx, ty = target

    # Greedy one-step move towards target with obstacle avoidance.
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        # Deterministic tie-breaker: minimize distance to target, then prefer moves that keep away from opponent.
        d_to = abs(nx - tx) + abs(ny - ty)
        d_opp = abs(nx - ox) + abs(ny - oy)
        cand = (d_to, -(d_opp), dx, dy)
        if best_move is None or cand < best_move[0]:
            best_move = (cand, [dx, dy])
    if best_move is None:
        return [0, 0]
    return best_move[1]
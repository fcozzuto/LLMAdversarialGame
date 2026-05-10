def choose_move(observation):
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Target selection: prefer resources we can reach no later than opponent; else maximize advantage.
    best = None
    best_key = None
    for tx, ty in resources:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # Aim: maximize (od - sd). Tie-break: minimize sd.
        key = (od - sd, -sd)
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best

    # Move selection: consider all 8 directions + stay; avoid obstacles; maximize immediate progress toward target.
    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_ms = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        nd = cheb(nx, ny, tx, ty)
        sd = cheb(sx, sy, tx, ty)
        # Encourage reducing distance; deterministic tie-break favors non-increasing then closer.
        progress = sd - nd  # positive is good
        ms = (progress, -nd, -abs((nx - tx)) - abs((ny - ty)))
        if best_ms is None or ms > best_ms:
            best_ms = ms
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
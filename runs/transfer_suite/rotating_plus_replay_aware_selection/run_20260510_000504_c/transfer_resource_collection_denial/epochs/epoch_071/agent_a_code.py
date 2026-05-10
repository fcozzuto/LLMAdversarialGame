def choose_move(observation):
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
        elif isinstance(p, dict):
            q = p.get("position", None)
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                obstacles.add((int(q[0]), int(q[1])))
            elif "x" in p and "y" in p:
                obstacles.add((int(p["x"]), int(p["y"])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            q = r.get("position", None)
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                resources.append((int(q[0]), int(q[1])))
            elif "x" in r and "y" in r:
                resources.append((int(r["x"]), int(r["y"])))

    def dist(a, b, c, d):
        return abs(a - b) + abs(c - d)

    # Pick resource I can likely collect first (minimize my distance, penalize if opponent is closer)
    target = None
    best_key = None
    for rx, ry in resources:
        md = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        key = (od - md, md)  # prefer where I am not worse; then closest
        if best_key is None or key < best_key:
            best_key, target = key, (rx, ry)

    if target is None:
        return [0, 0]

    rx, ry = target
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        # Greedy toward target with tie-break: also slightly avoid letting opponent become strictly closer next step
        my_next = dist(nx, ny, rx, ry)
        opp_next = dist(ox, oy, rx, ry)
        score = (my_next, (opp_next - my_next), abs(nx - ox) + abs(ny - oy))
        if best_score is None or score < best_score:
            best_score, best_move = score, [dx, dy]
    return best_move
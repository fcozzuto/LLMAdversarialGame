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

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    my = (sx, sy)
    opp = (ox, oy)
    best = None
    for t in resources:
        md = dist(my, t)
        od = dist(opp, t)
        # Prefer targets where I'm closer; if contested, choose where I'm less behind (or equal).
        margin = md - od
        key = (margin, md, -(abs(t[0] - ox) + abs(t[1] - oy)))
        if best is None or key < best[0]:
            best = (key, t)
    target = best[1]

    def inside(x, y):
        return 0 <= x < width and 0 <= y < height

    moves = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        nd = dist((nx, ny), target)
        # Mild preference: move that also reduces opponent distance to target, but primarily my distance.
        od = dist(opp, target)
        opp_step = dist(opp, (ox + dx, oy + dy)) if (inside(ox + dx, oy + dy) and (ox + dx, oy + dy) not in obstacles) else od
        score = (nd, od - opp_step, abs(nx - ox) + abs(ny - oy), dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]
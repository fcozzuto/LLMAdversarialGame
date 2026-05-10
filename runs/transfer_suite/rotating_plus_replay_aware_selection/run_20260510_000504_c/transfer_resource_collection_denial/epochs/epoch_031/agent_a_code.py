def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def best_for(pos):
        best = None
        for tx, ty in resources:
            if (tx, ty) in obstacles:
                continue
            self_d = abs(tx - pos[0]) + abs(ty - pos[1])
            opp_d = abs(tx - ox) + abs(ty - oy)
            if self_d < 1 and (tx, ty) in obstacles:
                continue
            # Race advantage: positive when we are closer; prefer nearer paths after accounting for contest.
            val = (opp_d - self_d) * 3 - self_d
            # Deterministic tie-break: prefer smaller (x,y)
            key = (val, -self_d, -(tx + ty), -tx, -ty)
            if best is None or key > best[0]:
                best = (key, (tx, ty))
        return best[1] if best else resources[0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    target = best_for((sx, sy))

    def clamp(nx, ny):
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            return None
        if (nx, ny) in obstacles:
            return None
        return (nx, ny)

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        ns = clamp(sx + dx, sy + dy)
        if ns is None:
            continue
        t = best_for(ns)
        self_d = abs(t[0] - ns[0]) + abs(t[1] - ns[1])
        opp_d = abs(t[0] - ox) + abs(t[1] - oy)
        # If opponent is about to grab it, try to switch to safer target.
        switch_pen = 6 if opp_d <= self_d else 0
        score = (opp_d - self_d) * 4 - self_d - switch_pen
        # Deterministic tie-break
        tieb = (score, -self_d, -(t[0] + t[1]), -dx, -dy)
        if best_score is None or tieb > best_score:
            best_score = tieb
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
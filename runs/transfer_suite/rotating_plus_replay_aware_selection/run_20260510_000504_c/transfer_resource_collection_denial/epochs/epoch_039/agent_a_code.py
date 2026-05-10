def choose_move(observation):
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources_raw = observation.get("resources", []) or []
    resources = []
    for r in resources_raw:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            if "position" in r and isinstance(r["position"], (list, tuple)) and len(r["position"]) >= 2:
                resources.append((int(r["position"][0]), int(r["position"][1])))
            elif "x" in r and "y" in r:
                resources.append((int(r["x"]), int(r["y"])))
    if not resources:
        return [0, 0]

    obstacles_raw = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
        elif isinstance(p, dict):
            if "position" in p and isinstance(p["position"], (list, tuple)) and len(p["position"]) >= 2:
                obstacles.add((int(p["position"][0]), int(p["position"][1])))
            elif "x" in p and "y" in p:
                obstacles.add((int(p["x"]), int(p["y"])))

    def clamp_step(nx, ny):
        if (nx, ny) in obstacles:
            return sx, sy
        return nx, ny

    def score_cell(cx, cy):
        # Prefer cells that let us be closer to a resource than opponent.
        best = -10**9
        for (rx, ry) in resources:
            sd = abs(rx - cx) + abs(ry - cy)
            od = abs(rx - ox) + abs(ry - oy)
            # Also slightly prefer moving toward resources closer to center-ish (tie-break stability).
            center = 7 - (abs(rx - 3) + abs(ry - 3))
            val = (od - sd) * 10 - sd + center * 0.01
            if val > best:
                best = val
        # Avoid going near opponent too closely (reduce collision/contested losses).
        best -= max(0, 4 - (abs(cx - ox) + abs(cy - oy))) * 2
        return best

    best_move = [0, 0]
    best_val = -10**18
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or ny < 0 or nx >= 8 or ny >= 8:
                nx, ny = sx, sy
            nx, ny = clamp_step(nx, ny)
            v = score_cell(nx, ny)
            # Deterministic tie-break: prefer fewer steps, then lexicographic.
            step_cost = abs(nx - sx) + abs(ny - sy)
            v_key = (v, -step_cost, -nx, -ny)
            if v_key > (best_val, 0, 0, 0):
                best_val = v
                best_move = [dx if (nx != sx or ny != sy) else 0, dy if (nx != sx or ny != sy) else 0]

    return [int(best_move[0]), int(best_move[1])]
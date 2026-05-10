def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    selfT = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opT = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))

    sc_self = float(observation.get("self_territory_count", len(selfT)) or 0)
    sc_op = float(observation.get("opponent_territory_count", len(opT)) or 0)
    behind = sc_self + 0.01 < sc_op

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if behind:
        tx, ty = ox, oy
    else:
        un = observation.get("unclaimed_cells") or []
        best_u = None
        best_d = 10**18
        for i, p in enumerate(un):
            if i >= 40:
                break
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                ux, uy = int(p[0]), int(p[1])
                d = abs(ux - sx) + abs(uy - sy)
                # Prefer closer and towards center (deterministic among ties)
                cd = (abs(ux - cx) + abs(uy - cy)) * 0.05
                score = d + cd
                if score < best_d:
                    best_d = score
                    best_u = (ux, uy)
        tx, ty = (best_u if best_u else (int(cx), int(cy)))

    best_move = [0, 0]
    best_val = -10**30
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d_t = abs(tx - nx) + abs(ty - ny)
        d_o = abs(ox - nx) + abs(oy - ny)
        center_pen = ((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)) * 0.001
        # Aggressive: get closer to opponent; Defensive/Expand: get closer to target, keep distance from opponent
        val = (-d_t if behind else -d_t + 0.15 * d_o) - center_pen
        # Prefer deterministic non-opponent moves when equal
        if val > best_val or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = val
            best_move = [dx, dy]

    return best_move
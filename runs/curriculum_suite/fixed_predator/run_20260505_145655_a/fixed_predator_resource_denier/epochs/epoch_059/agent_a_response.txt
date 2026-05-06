def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            obstacles.add((x, y))
    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Choose a "deny" focus: resources where opponent is relatively close vs us.
    best_focus = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Strongly prefer places where opponent is closer; tie-break toward our ability to reach quickly.
        t = ((od - sd), -sd, -od, rx, ry)
        if best_focus is None or t > best_focus:
            best_focus = t
    tx, ty = best_focus[3], best_focus[4]

    # One-step lookahead: pick move maximizing deny-score over resources, centered on focus.
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        # If we somehow select (0,0) it will be fine; otherwise avoid obstacle.
        val = -10**18
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            deny = (od - sd)
            # Emphasize denial at focus resource; slightly also consider overall denial.
            focus_boost = 2.5 if (rx == tx and ry == ty) else 0.0
            # Penalize large distance to keep pressure.
            v = (deny * 6.0 + focus_boost * (deny * 4.0) - sd * 0.7)
            # Small tie-break: stay away from giving opponent too much safety (prefer moves that increase od-sd gap).
            if v > val:
                val = v
        # Prefer moves that reduce distance to focus when denial is tied.
        if val == val:  # keep deterministic flow
            tieb = -man(nx, ny, tx, ty)
            v2 = val + tieb * 0.05
        else:
            v2 = val
        if best_val is None or v2 > best_val:
            best_val = v2
            best_move = [dx, dy]

    # If all moves were invalid (surrounded by obstacles), allow staying.
    return best_move if best_move != [0, 0] or (sx, sy) not in obstacles else [0, 0]
def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    self_role = str(observation.get("self_role", "")).lower()
    opponent_role = str(observation.get("opponent_role", "")).lower()
    pursuer_me = ("pursuer" in self_role) or ("evader" not in self_role and "pursuer" in opponent_role) or ("pursuit" in self_role and "evad" not in self_role)

    dxdy = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist2(a, b, c, d):
        dx, dy = a - c, b - d
        return dx*dx + dy*dy

    # Predict opponent tendency (pursuit_direct): likely moving toward/away from us; approximate by aiming one step along its direction to our position.
    # If we are pursuer, we chase; if evader, we flee.
    ex, ey = ox, oy
    step_to_us_x = 0 if sx == ox else (1 if sx > ox else -1)
    step_to_us_y = 0 if sy == oy else (1 if sy > oy else -1)
    predicted_x = ex + step_to_us_x
    predicted_y = ey + step_to_us_y
    if not inb(predicted_x, predicted_y) or (predicted_x, predicted_y) in blocked:
        predicted_x, predicted_y = ex, ey

    best_move = (0, 0)
    best_val = None
    # Deterministic tie-break order based on deltas
    for dx, dy in dxdy:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        d = dist2(nx, ny, predicted_x, predicted_y)
        val = -d if pursuer_me else d
        # Small bias: prefer moves that reduce/enhance Manhattan toward predicted (stable tie-break)
        man = abs(nx - predicted_x) + abs(ny - predicted_y)
        val = val * 1000 + (-man if pursuer_me else man)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
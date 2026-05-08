def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles", [])
    cap_r = observation.get("capture_radius", 0)
    self_role = (observation.get("self_role", "") or "").lower()

    obs = {(o[0], o[1]) for o in obstacles if isinstance(o, (list, tuple)) and len(o) >= 2}
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y): 
        return 0 <= x < w and 0 <= y < h

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    is_pursuer = ("pursuer" in self_role) or ("catch" in self_role) or ("chaser" in self_role)
    # For evader: pick a "run-to" corner opposite the pursuer with a parity offset to induce zigzag.
    if not is_pursuer:
        corner_x = (w - 1 - ox)
        corner_y = (h - 1 - oy)
        run_x = max(0, min(w - 1, corner_x))
        run_y = max(0, min(h - 1, corner_y))
        # Snap target to a corner-ish position to keep determinism.
        if run_x < (w - 1) / 2: run_x = 0
        else: run_x = w - 1
        if run_y < (h - 1) / 2: run_y = 0
        else: run_y = h - 1
        # Use step parity to vary between the two best adjacent escapes deterministically.
        parity = observation.get("turn_index", 0) & 1
    else:
        parity = observation.get("turn_index", 0) & 1

    best = None
    best_score = None
    # Deterministic tie-break: fixed move order, then lexicographic.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obs:
            continue
        captured = (cap_r == 0 and nx == ox and ny == oy) or (cap_r != 0 and dist2(nx, ny, ox, oy) <= cap_r * cap_r)
        if captured:
            score = float("inf") if is_pursuer else float("-inf")
        else:
            d2 = dist2(nx, ny, ox, oy)
            # Local obstacle pressure: prefer moves with more free neighbors for evader,
            # less free neighbors for pursuer (to box them in).
            free = 0
            for ddx, ddy in moves:
                tx, ty = nx + ddx, ny + ddy
                if inb(tx, ty) and (tx, ty) not in obs:
                    free += 1
            if is_pursuer:
                # Pursuer: strongly reduce distance, and secondarily reduce evader mobility.
                score = (-d2) + (-0.03 * free) + (0.001 * parity * (nx + ny))
            else:
                # Evader: maximize distance, keep momentum away from opponent, and avoid dead-ends.
                # Bias toward run-to target but allow zigzag via parity penalty on "straight" direction.
                txd = dist2(nx, ny, run_x, run_y)
                # Zigzag: discourage repeating direction towards the pursuer; encourage perpendicular shift.
                to_ox = (nx - ox, ny - oy)
                dot = (to_ox[0] * dx + to_ox[1] * dy)
                zig_pen = 0.01 * parity * dot
                score = (d2) + (0.02 * free) + (0.001 * (-txd)) - zig_pen
        if best_score is None or (score > best_score if not is_pursuer else score > best_score):
            best_score = score
            best = [dx, dy]
        elif score == best_score:
            if [dx, dy] < best:
                best = [dx, dy]

    if best is None:
        return [0, 0]
    return best
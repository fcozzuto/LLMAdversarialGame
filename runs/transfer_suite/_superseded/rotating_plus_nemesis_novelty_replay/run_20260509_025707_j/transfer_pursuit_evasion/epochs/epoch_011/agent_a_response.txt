def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]

    sp = observation.get("self_position")
    op = observation.get("opponent_position")
    if not isinstance(sp, (list, tuple)) or not isinstance(op, (list, tuple)) or len(sp) < 2 or len(op) < 2:
        return [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for o in observation.get("obstacles") or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    def man(a, b, c, d):  # (a,b) to (c,d)
        return abs(a - c) + abs(b - d)
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    # Evader corner target (likely): nearest corner to opponent
    tcx, tcy = min(corners, key=lambda c: man(ox, oy, c[0], c[1]))

    role = (observation.get("self_role") or "pursuer").lower()
    evader = (role == "evader")

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_dx, best_dy = 0, 0
    best_val = None

    # Pursuer: minimize distance to opponent while also getting closer to target corner (cutoff).
    # Evader: maximize distance to opponent while drifting away from target corner.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_opp = man(nx, ny, ox, oy)
        d_corner = man(nx, ny, tcx, tcy)
        d_corner_opp = man(ox, oy, tcx, tcy)

        # Add progress pressure: if opponent is closer to corner, we should reduce our distance to that corner.
        # If already at/near that corner, focus on opponent capture pressure.
        corner_weight = 1.0 + (d_corner_opp / max(1, (w + h - 2)))
        if evader:
            val = (d_opp * 3.0) - (d_corner * 0.9 * corner_weight)
        else:
            val = (d_opp * 1.6) + (d_corner * 0.9 * corner_weight)

        # Deterministic tie-break via move order: choose first best.
        if best_val is None or (val < best_val) != evader:
            best_val = val
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]
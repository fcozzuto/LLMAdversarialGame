def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    turns_remaining = observation.get("turns_remaining", 0)

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist_manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def clamp_move(nx, ny):
        return [nx - sx, ny - sy]

    if not resources:
        return [0, 0]

    late = 1.0 if turns_remaining <= 10 else 0.0
    # Prefer resources where we can arrive earlier; late game prefer just nearest for self.
    best_r = None
    best_score = None
    for rx, ry in resources:
        md = dist_manh(sx, sy, rx, ry)
        od = dist_manh(ox, oy, rx, ry)
        # Higher is better
        # Early: racing advantage dominates; Late: minimize self distance.
        race = (od - md)  # positive if we are closer
        score = (race * 10.0) + (-md * (1.5 - late)) + (-od * (0.2 if late == 0 else 0.05))
        if best_score is None or score > best_score:
            best_score = score
            best_r = (rx, ry)

    tx, ty = best_r

    # Try 9 possible deltas, choose the one that maximizes score toward target and beats opponent.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = None
    best_m_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        md_t = dist_manh(nx, ny, tx, ty)
        od_t = dist_manh(ox, oy, tx, ty)
        # Encourage improving our lead to the chosen target; discourage getting closer for opponent.
        lead_now = (od_t - md_t)
        # If stepping onto any resource, strongly prefer it.
        on_res = 1 if (nx, ny) in set(tuple(r) for r in resources) else 0
        # Small tie-break toward staying centered (reduce oscillation): prefer not moving diagonally unless needed.
        diag_pen = 0.2 if dx != 0 and dy != 0 else 0.0
        sc = (on_res * 1e6) + (lead_now * 12.0) + (-md_t * (2.0 + late)) - diag_pen
        if best_m_score is None or sc > best_m_score:
            best_m_score = sc
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]
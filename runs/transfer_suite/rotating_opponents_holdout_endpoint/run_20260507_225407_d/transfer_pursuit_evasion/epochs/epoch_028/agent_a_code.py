def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    is_pursuer = ("pursuer" in self_role) or ("pursue" in self_role) or (("pursuit" in self_role) and ("evasion" not in self_role))
    is_evader = ("evader" in self_role) or ("evasion" in self_role) or ("escape" in self_role)
    if not is_pursuer and not is_evader:
        is_pursuer = ("pursuer" in opp_role) or ("pursue" in opp_role)
        is_evader = not is_pursuer

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (x, y) in obstacles

    def obs_pen(x, y):
        if blocked(x, y):
            return 10**7
        pen = 0
        for (px, py) in obstacles:
            d = abs(px - x) + abs(py - y)
            if d == 0: return 10**7
            if d == 1: pen += 4
            elif d == 2: pen += 2
        return pen

    best = None
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        d_to_opp = max(abs(ox - nx), abs(oy - ny))  # capture_radius=0, use Chebyshev for diagonal moves
        d_to_obs = obs_pen(nx, ny)
        if is_evader:
            # Prefer increasing distance from pursuer; avoid obstacles; prefer moving toward corners farther from opponent.
            corner_score = 0
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            for cx, cy in corners:
                corner_score = max(corner_score, abs(cx - nx) + abs(cy - ny))
            val = (-d_to_opp) + d_to_obs * 3 - corner_score * 0.01
            # We want maximize; invert by negating into minimize below
        else:
            # Pursuer: minimize distance to opponent while avoiding obstacles.
            val = d_to_opp + d_to_obs * 5
        # Deterministic tie-break: lowest val, then preferring larger dx, then larger dy, then 0,0 is naturally handled by ordering.
        minimize = val
        if best is None or minimize < best_val:
            best_val = minimize
            best = [dx, dy]

    if best is None:
        # If all moves blocked (unlikely), deterministically stay put.
        return [0, 0]
    return best
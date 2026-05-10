def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    obs = set((int(p[0]), int(p[1])) for p in obstacles)

    def role_is_purs(role):
        r = (role or "").lower()
        if "purs" in r:
            return True
        if "evad" in r:
            return False
        return None

    sr = role_is_purs(observation.get("self_role"))
    orr = role_is_purs(observation.get("opponent_role"))
    if sr is None:
        sr = (orr is False)
    i_am_pursuer = bool(sr)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def d2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    # For pursuer: opp is trying to escape to a corner; bias toward that corner.
    corner_for_opp = min(corners, key=lambda c: d2(ox, oy, c[0], c[1]))
    # For evader: run to farthest corner from pursuer.
    corner_flee = max(corners, key=lambda c: d2(ox, oy, c[0], c[1]))

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Obstacle clearance: prefer not to step into tight cells.
        min_obs = 10**9
        for (px, py) in obs:
            t = d2(nx, ny, px, py)
            if t < min_obs:
                min_obs = t
        clearance = min_obs  # larger is better

        if i_am_pursuer:
            # Primary: get closer to opponent.
            base = d2(nx, ny, ox, oy)
            # Secondary: move so that we naturally intercept towards opp's nearest corner.
            intercept = d2(nx, ny, corner_for_opp[0], corner_for_opp[1])
            val = base * 1.0 + intercept * 0.15 - clearance * 0.02
        else:
            # Evader: maximize distance from opponent, keep moving toward a good corner.
            base = d2(nx, ny, ox, oy)
            toward = d2(nx, ny, corner_flee[0], corner_flee[1])
            # If already at the corner, keep maximizing escape distance.
            val = -base * 1.0 + toward * 0.05 - clearance * 0.03

        if best is None:
            best, best_val = [dx, dy], val
        else:
            if i_am_pursuer:
                if val < best_val:
                    best, best_val = [dx, dy], val
            else:
                if val < best_val:
                    best, best_val = [dx, dy], val

    return best if best is not None else [0, 0]
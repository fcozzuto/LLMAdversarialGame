def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        a = abs(x1 - x2)
        b = abs(y1 - y2)
        return a if a > b else b

    obs_list = list(blocked)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    role = (observation.get("self_role") or "").lower()
    is_evader = ("evad" in role) or ("runner" in role) or ("escape" in role) or ("hide" in role) or ("evader" in role)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
    target_x, target_y = (far_corner if is_evader else (ox, oy))

    def min_obs_d(x, y):
        if not obs_list:
            return 5
        m = 10**9
        for bx, by in obs_list:
            d = cheb(x, y, bx, by)
            if d < m:
                m = d
        return m if m != 10**9 else 5

    best = None
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        dist_opp = cheb(nx, ny, ox, oy)
        dist_t = cheb(nx, ny, target_x, target_y)
        d_obs = min_obs_d(nx, ny)
        # Greedy pursue/evasion with obstacle safety and tie-breaking toward alignment.
        if is_evader:
            val = (dist_opp * 10) + (dist_t * 2) + (d_obs * 0.5)
            val += -0.01 * cheb(nx, ny, ox, oy)  # small deterministic nudge
        else:
            val = (-dist_opp * 10) + (-dist_t * 2) + (d_obs * 0.5)
            # Prefer moves that reduce distance to opponent more than to target (target==opp when not evader).
            val += -0.01 * cheb(nx, ny, ox, oy)
        if best is None or val > best_val:
            best_val = val
            best = [dx, dy]

    return best if best is not None else [0, 0]
def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for b in obstacles:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            obs.add((int(b[0]), int(b[1])))

    role = (observation.get("self_role", "") or "").lower()
    evader = ("evader" in role) or ("escape" in role) or ("runner" in role) or ("flee" in role)

    actions = [(-1, -1), (-1, 0), (-1, 1),
               (0, -1), (0, 0), (0, 1),
               (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obs
    def d2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy
    def clearance(x, y):
        # min Chebyshev distance to obstacles; higher is safer
        m = 10**9
        for bx, by in obs:
            cd = abs(x - bx) if abs(x - bx) > abs(y - by) else abs(y - by)
            if cd < m:
                m = cd
        return 0 if not obs else m

    candidates = []
    for dx, dy in actions:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            dist = d2(nx, ny, ox, oy)
            clr = clearance(nx, ny)
            # Prefer moves that decrease distance if pursuer; increase if evader
            # Tie-break deterministically toward larger clearance and toward center.
            cx = (w - 1) / 2.0
            cy = (h - 1) / 2.0
            center_pen = d2(nx, ny, cx, cy)
            score = (-dist if not evader else dist) + 0.05 * clr - 1e-3 * center_pen
            candidates.append((score, dx, dy, nx, ny))

    if not candidates:
        return [0, 0]

    # Deterministic: choose max score, then fixed order of moves
    # (use dx,dy as final tie-break)
    candidates.sort(key=lambda t: (t[0], -t[1], -t[2], t[3], t[4]), reverse=True)
    _, dx, dy, _, _ = candidates[0]
    return [int(dx), int(dy)]
def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = (observation.get("self_role", "") or "").lower()
    env = (observation.get("environment_name", "") or "").lower()
    is_evader = any(k in role for k in ("evader", "runner", "evade", "escape"))
    if any(k in env for k in ("evader", "runner", "evade", "escape")):
        is_evader = True
    is_evader = not is_evader  # default to pursuer unless explicitly evader-like

    blocked = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    far_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    best = None
    bestv = -10**18 if is_evader else 10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        d = dist2(nx, ny, ox, oy)
        if is_evader:
            primary = d
            sec = dist2(nx, ny, far_corner[0], far_corner[1])
            # avoid moving "toward" pursuer while also drifting to far corner
            toward = (abs(nx - ox) + abs(ny - oy))
            v = primary + 0.02 * sec + 0.001 * toward
            if v > bestv:
                bestv, best = v, [dx, dy]
        else:
            primary = -d
            sec = - (abs(nx - ox) + abs(ny - oy))
            # for wall-running evasion, bias toward cutting off by heading to far corner
            tc = dist2(nx, ny, far_corner[0], far_corner[1])
            v = primary + 0.01 * sec - 0.001 * tc
            if v < bestv:
                bestv, best = v, [dx, dy]

    if best is None:
        return [0, 0]
    return best
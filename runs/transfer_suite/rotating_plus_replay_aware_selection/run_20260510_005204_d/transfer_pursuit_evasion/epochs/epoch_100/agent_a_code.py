def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "")).lower()
    is_evader = any(k in role for k in ["evader", "runner", "evade", "escape"])
    env = str(observation.get("environment_name", "")).lower()
    if any(k in env for k in ["evader", "runner", "evade", "escape"]):
        is_evader = True

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    if is_evader:
        target = max(corners, key=lambda c: (abs(c[0] - ox) + abs(c[1] - oy), -dist2(c[0], c[1], sx, sy)))
        tx, ty = target
        best = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in blocked:
                continue
            # Prefer increasing distance from pursuer, and also moving toward the chosen far corner.
            score = dist2(nx, ny, ox, oy) * 10 - dist2(nx, ny, tx, ty) - (dist2(nx, ny, sx, sy) * 0.01)
            if best is None or score > best[0]:
                best = (score, dx, dy)
        if best is None:
            return [0, 0]
        return [int(best[1]), int(best[2])]

    # Pursuer: minimize distance to evader (opponent), avoid obstacles, and do slight "corner pressure".
    target = max(corners, key=lambda c: -dist2(c[0], c[1], ox, oy))
    cx, cy = target
    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        score = -dist2(nx, ny, ox, oy) * 10 + dist2(nx, ny, cx, cy) * 0.02
        if best is None or score > best[0]:
            best = (score, dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]
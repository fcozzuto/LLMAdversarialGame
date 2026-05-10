def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [sx, sy]) or [sx, sy]
    sx, sy = int(sx), int(sy)
    ox, oy = int(ox), int(oy)

    obs = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    resources = observation.get("resources", []) or []
    best_targets = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            tx, ty = int(p[0]), int(p[1])
            if inb(tx, ty) and (tx, ty) not in obs:
                best_targets.append((tx, ty))
    if best_targets:
        tx, ty = min(best_targets, key=lambda t: (abs(t[0] - sx) + abs(t[1] - sy), t[0], t[1]))
    else:
        tx, ty = w // 2, h // 2

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def score(nx, ny):
        if not inb(nx, ny) or (nx, ny) in obs:
            return -10**9
        d_own = abs(tx - nx) + abs(ty - ny)
        d_opp = abs(ox - nx) + abs(oy - ny)
        return -d_own + 0.15 * d_opp

    best = None
    best_s = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        s = score(nx, ny)
        if s > best_s:
            best_s = s
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]
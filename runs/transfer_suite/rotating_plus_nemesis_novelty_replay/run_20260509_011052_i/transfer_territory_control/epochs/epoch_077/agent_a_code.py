def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy = int(sx), int(sy)
    ox, oy = int(ox), int(oy)

    obs_cells = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs_cells.add((int(p[0]), int(p[1])))

    resources = []
    for p in (observation.get("resources", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resources.append((int(p[0]), int(p[1])))
    unclaimed = []
    for p in (observation.get("unclaimed_cells", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.append((int(p[0]), int(p[1])))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    targets = resources if resources else unclaimed if unclaimed else [(cx, cy), (ox, oy)]

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    best = None
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    target = None
    bestt = None
    for t in targets:
        tt = dist2((sx, sy), (t[0], t[1]))
        if bestt is None or tt < bestt:
            bestt = tt
            target = (t[0], t[1])

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs_cells:
            continue
        d_to_target = dist2((nx, ny), target)
        d_to_opp = dist2((nx, ny), (ox, oy))
        score = d_to_target - 0.12 * d_to_opp
        if best is None or score < best:
            best = score
            best_move = [dx, dy]

    if best is not None:
        return best_move

    # Fallback: deterministic move toward clamped center
    tx, ty = int(round(cx)), int(round(cy))
    dx = clamp(tx - sx, -1, 1)
    dy = clamp(ty - sy, -1, 1)
    if dx == 0 and dy == 0:
        dx = 1 if sx < w - 1 else -1 if sx > 0 else 0
        dy = 1 if sy < h - 1 else -1 if sy > 0 else 0
    nx, ny = sx + dx, sy + dy
    if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_cells:
        return [dx, dy]
    return [0, 0]
def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def dist_cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    # Pick a resource we can reach first (deny opponent when possible), deterministic tie-breaks.
    best = None
    best_key = None
    for p in resources:
        tx, ty = int(p[0]), int(p[1])
        if not (0 <= tx < w and 0 <= ty < h) or (tx, ty) in obs:
            continue
        ds = dist_cheb(sx, sy, tx, ty)
        do = dist_cheb(ox, oy, tx, ty)
        # Primary: maximize denial window (opp - self); Secondary: minimize self distance.
        key = (do - ds, -ds, -((tx + ty) & 1), -((tx * 31 + ty) & 1023), tx, ty)
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best
    # Move one step toward target while avoiding obstacles; deterministic among ties.
    candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        d = dist_cheb(nx, ny, tx, ty)
        # Prefer reducing distance; also keep symmetry-breaking deterministic.
        step_key = (-d, dx, dy, nx, ny)
        candidates.append((step_key, [dx, dy]))
    candidates.sort(reverse=True, key=lambda t: t[0])
    if candidates:
        return candidates[0][1]
    return [0, 0]
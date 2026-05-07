def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    if not resources:
        return [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Pick a target that we can reach earlier than opponent; tie-break by closeness and parity.
    best = None
    best_key = None
    for p in resources:
        tx, ty = int(p[0]), int(p[1])
        if not (0 <= tx < w and 0 <= ty < h):
            continue
        if (tx, ty) in obs:
            continue
        ds = md(sx, sy, tx, ty)
        do = md(ox, oy, tx, ty)
        # Prefer strong denial; slight bias to nearer targets and checkerboard for stability.
        key = ((do - ds), -(ds), -((tx + ty) & 1), -tx, -ty)
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)

    if best is None:
        return [0, 0]
    tx, ty = best

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    bestm = None
    bestmk = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        # After move: aim to reduce our distance while also not giving opponent an immediate advantage.
        ns = md(nx, ny, tx, ty)
        no = md(ox, oy, tx, ty)
        denial_after = no - ns
        # Penalize getting closer to obstacles to reduce accidental stalls.
        obs_pen = 0
        for ax, ay in obs:
            if abs(ax - nx) <= 1 and abs(ay - ny) <= 1:
                obs_pen += 1
        # Small deterministic tie-breaker by direction.
        key = (denial_after, -ns, -obs_pen, dx, dy, (nx + ny) & 1)
        if bestmk is None or key > bestmk:
            bestmk = key
            bestm = (dx, dy)

    if bestm is None:
        return [0, 0]
    dx, dy = bestm
    return [int(dx), int(dy)]
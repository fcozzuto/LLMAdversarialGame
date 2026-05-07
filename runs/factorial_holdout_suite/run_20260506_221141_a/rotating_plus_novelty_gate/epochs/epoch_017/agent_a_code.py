def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    obstacles = observation.get("obstacles", []) or []
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    dirs = [(0, -1), (1, 0), (0, 1), (-1, 0), (0, 0)]
    best = [0, 0]
    bestv = -10**18

    # Deterministically pick a target:
    # Prefer resources where we are closer than opponent; else pick the resource opponent is closest to.
    best_t = None
    best_gap = -10**18
    best_opp = 10**18
    for p in resources:
        tx, ty = int(p[0]), int(p[1])
        if not (0 <= tx < w and 0 <= ty < h):
            continue
        dS = md(sx, sy, tx, ty)
        dO = md(ox, oy, tx, ty)
        gap = dO - dS  # positive means we are closer
        if gap > 0:
            if gap > best_gap:
                best_gap = gap
                best_t = (tx, ty)
        else:
            if best_t is None and dO < best_opp:
                best_opp = dO
                best_t = (tx, ty)
    if best_t is None:
        best_t = (int(resources[0][0]), int(resources[0][1]))

    tx, ty = best_t
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        dS2 = md(nx, ny, tx, ty)
        dO2 = md(ox, oy, tx, ty)
        # Value: reduce our distance; if we can't win, still move to deny (increase opponent deficit).
        # Small obstacle-neighborhood penalty to avoid getting trapped.
        neigh = 0
        for ax, ay in ((nx-1, ny), (nx+1, ny), (nx, ny-1), (nx, ny+1)):
            if (ax, ay) in obs:
                neigh += 1
        v = (dO2 - dS2) * 1000 - dS2 - neigh
        if v > bestv:
            bestv = v
            best = [dx, dy]
    return best
def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        try:
            obs.add((p[0], p[1]))
        except:
            continue

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_key = None

    for rx, ry in resources:
        if rx < 0 or ry < 0 or rx >= w or ry >= h:
            continue
        sd = abs(sx - rx) if abs(sx - rx) > abs(sy - ry) else abs(sy - ry)
        od = abs(ox - rx) if abs(ox - rx) > abs(oy - ry) else abs(oy - ry)
        adv = od - sd
        key = (-(adv * 1000 - sd), rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]

    rx, ry = best
    # If we can step onto a resource (adjacent), prioritize it.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            for pr, py in resources:
                if nx == pr and ny == py:
                    return [dx, dy]

    # Otherwise move to minimize our Chebyshev distance to target, with deterministic tie-break.
    curd = abs(sx - rx) if abs(sx - rx) > abs(sy - ry) else abs(sy - ry)
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        nd = abs(nx - rx) if abs(nx - rx) > abs(ny - ry) else abs(ny - ry)
        od = abs(ox - rx) if abs(ox - rx) > abs(oy - ry) else abs(oy - ry)
        # Prefer smaller nd; if tie, prefer larger advantage (opponent farther); if tie, deterministic by dx,dy order.
        val = (nd, -(od - nd), dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        return [0, 0]
    return [dx, dy]
def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick a resource we can reach with advantage; tie-break by closer overall.
    best_t = None
    best_key = None
    for tx, ty in resources:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        key = (sd - od, sd, od, tx, ty)  # smaller is better
        if best_key is None or key < best_key:
            best_key = key
            best_t = (tx, ty)

    tx, ty = best_t

    # Move to minimize distance to target; avoid obstacles; tie-break by staying farther from opponent.
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = (0, 0)
    best_mkey = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        nd = cheb(nx, ny, tx, ty)
        oppd = cheb(nx, ny, ox, oy)
        mkey = (nd, -oppd, abs(dx) + abs(dy), dx, dy)
        if best_mkey is None or mkey < best_mkey:
            best_mkey = mkey
            best_m = (dx, dy)

    if best_mkey is None:
        # All moves hit obstacles or bounds; try staying if possible.
        if (sx, sy) in obs:
            # Shouldn't happen, but deterministic fallback.
            return [0, 0]
        return [0, 0]

    return [int(best_m[0]), int(best_m[1])]
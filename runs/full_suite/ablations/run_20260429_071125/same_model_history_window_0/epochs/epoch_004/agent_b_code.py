def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    if (sx, sy) in resources:
        return [0, 0]

    def dist_cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy  # squared Chebyshev not needed; squared Euclidean works monotonic

    cur_d = dist_cheb(sx, sy, ox, oy)

    best = None
    best_val = -10**18
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = dist_cheb(sx, sy, rx, ry)
        do = dist_cheb(ox, oy, rx, ry)
        # Favor resources where we are relatively closer; deterministic tie-breaker on ds
        val = (do - ds) * 1000 - ds
        if val > best_val or (val == best_val and (best is None or ds < best[0])):
            best_val = val
            best = (ds, rx, ry)

    if best is None:
        return [0, 0]
    _, tx, ty = best

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            dnew = dist_cheb(nx, ny, tx, ty)
            dcur = dist_cheb(sx, sy, tx, ty)
            # Prefer moving closer to target; slight preference to increase distance from opponent
            score = (dcur - dnew) * 1000 + (dist_cheb(nx, ny, ox, oy) - cur_d)
            candidates.append((score, dnew, dx, dy))
    if not candidates:
        return [0, 0]
    candidates.sort(reverse=True, key=lambda t: (t[0], -t[1], t[2], t[3]))
    return [int(candidates[0][2]), int(candidates[0][3])]
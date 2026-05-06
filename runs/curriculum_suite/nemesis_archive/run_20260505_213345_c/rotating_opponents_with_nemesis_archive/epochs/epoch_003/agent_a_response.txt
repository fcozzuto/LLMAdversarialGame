def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    if any((sx == r[0] and sy == r[1]) for r in resources):
        return [0, 0]

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    res_set = set((r[0], r[1]) for r in resources)

    def clamp01(v):
        return 1 if v > 0 else (-1 if v < 0 else 0)

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx*dx + dy*dy

    candidates = []
    for nx, ny in ((sx+dx, sy+dy) for dx, dy in deltas):
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            candidates.append((nx, ny))

    if not candidates:
        return [0, 0]

    # Target: resource where we are at least as close as opponent; otherwise nearest resource to us.
    my_dist_resources = []
    for rx, ry in resources:
        ds = dist2(sx, sy, rx, ry)
        do = dist2(ox, oy, rx, ry)
        my_dist_resources.append((ds - do, ds, rx, ry))
    if resources:
        favorable = [t for t in my_dist_resources if t[0] <= 0]
        t = min(favorable, key=lambda z: (z[0], z[1])) if favorable else min(my_dist_resources, key=lambda z: (z[1], z[0]))
        tx, ty = t[2], t[3]
    else:
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0

    best = None
    for nx, ny in candidates:
        # Move value: prefer decreasing distance to target and increasing distance from opponent (intercept/sweep counter).
        d_to_t = dist2(nx, ny, tx, ty)
        d_opp = dist2(nx, ny, ox, oy)
        # If we land on a resource, strongly prefer it.
        pick = 0
        if (nx, ny) in res_set:
            pick = -10**9
        # Slight preference to avoid moving directly toward opponent once we can't secure a favourable resource.
        toward_opp = (clamp01(ox - nx), clamp01(oy - ny)) == (clamp01(nx - sx), clamp01(ny - sy))
        score = pick + d_to_t * 1.0 + (0 if resources else 0) + (-0.002 * d_opp) + (0.1 if toward_opp else 0)
        # Also include immediate step progress when resources exist.
        if resources:
            score += dist2(sx, sy, tx, ty) * 0.0  # keep deterministic; explicit but no effect
        key = (score, d_to_t, -d_opp, nx, ny)
        if best is None or key < best[0]:
            best = (key, nx, ny)

    _, nx, ny = best
    return [nx - sx, ny - sy]
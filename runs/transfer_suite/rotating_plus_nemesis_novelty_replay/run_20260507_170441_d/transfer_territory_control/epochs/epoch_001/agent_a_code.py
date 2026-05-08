def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = observation.get("obstacles", [])
    obs_set = set((x, y) for x, y in obstacles)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    unclaimed = observation.get("unclaimed_cells", [])
    # Deterministically sample a few unclaimed targets closest to us
    t = []
    for p in unclaimed:
        x, y = p
        d = abs(x - sx) + abs(y - sy)
        t.append((d, x, y))
    t.sort()
    targets = [(x, y) for _, x, y in t[:8]] if t else []

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    order = {d: i for i, d in enumerate(dirs)}
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs_set:
            continue
        # prefer moving away from opponent
        dist_opp = abs(nx - ox) + abs(ny - oy)
        # prefer moving toward unclaimed (small deterministic boost)
        dist_unc = 0
        if targets:
            dist_unc = min(abs(nx - x) + abs(ny - y) for x, y in targets)
        # also mildly prefer center
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        dist_center = abs(nx - cx) + abs(ny - cy)

        val = dist_opp * 1000 + (-dist_unc) * 10 + (-dist_center)
        if val > best_val or (val == best_val and order[(dx, dy)] < order[best_move]):
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]
def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [7, 7])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources_in = observation.get("resources", []) or []
    obstacles_in = observation.get("obstacles", []) or []

    obstacles = set()
    for p in obstacles_in:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in resources_in:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resources.append((int(p[0]), int(p[1])))
    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def best_target():
        best = None
        best_key = None
        for rx, ry in resources:
            sd = man(sx, sy, rx, ry)
            od = man(ox, oy, rx, ry)
            lead = od - sd  # positive means we are closer
            # tie-break: prefer positive lead; then smaller our distance; then deterministic coordinate bias
            key = (lead > 0, lead, -sd, -rx, -ry)
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        return best

    tx, ty = best_target()

    # Move choice: try to reduce our distance to target; if blocked, sidestep; if still blocked, choose least-bad.
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def eval_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            return None
        if (nx, ny) in obstacles:
            return None
        d = man(nx, ny, tx, ty)
        # Slightly penalize moving closer to opponent when tie/close lead, to avoid being out-raced
        od_now = man(ox, oy, tx, ty)
        od_next = man(ox, oy, tx, ty)  # opponent stationary this step
        lead_next = od_next - d
        opp_dist_pen = man(nx, ny, ox, oy)
        return (d, -(lead_next > 0), -lead_next, opp_dist_pen)

    best = None
    best_val = None
    for dx, dy in dirs:
        v = eval_move(dx, dy)
        if v is None:
            continue
        if best_val is None or v < best_val:
            best_val = v
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]
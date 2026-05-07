def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    if not w or not h:
        return [0, 0]
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    # Precompute adjacency to obstacles to discourage edge-strafing into traps
    def adj_obst(x, y):
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            if (x + dx, y + dy) in obs:
                return 1
        return 0

    if not resources:
        # Fallback: move toward opponent corner-ish deterministically to reduce distance
        tx = 0 if ox > sx else w - 1
        ty = 0 if oy > sy else h - 1
        best_dxdy = (0, 0)
        best_d = 10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            d = abs(nx - tx) + abs(ny - ty)
            if d < best_d:
                best_d = d
                best_dxdy = (dx, dy)
        return [best_dxdy[0], best_dxdy[1]]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        self_best = -10**18
        # Evaluate by how much closer we are than opponent for the best contested resource
        for rx, ry in resources:
            if not inb(rx, ry):
                continue
            sd = abs(nx - rx) + abs(ny - ry)
            od = abs(ox - rx) + abs(oy - ry)

            capture_bonus = 1000 if (nx == rx and ny == ry) else 0
            # Prefer resources where we are (or will be) closer than opponent
            score = capture_bonus + (od - sd) * 20 - sd - self_best * 0  # keep deterministic
            if score > self_best:
                self_best = score

        # Mild penalty for being adjacent to obstacles; tie-break deterministically by move order
        penalty = adj_obst(nx, ny) * 2
        total = self_best - penalty

        if total > best_score:
            best_score = total
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]
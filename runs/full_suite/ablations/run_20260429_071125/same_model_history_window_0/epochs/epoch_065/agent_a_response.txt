def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    # Choose best resource: maximize (opp_dist - self_dist), then minimize self_dist
    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            sd = dist2(sx, sy, rx, ry)
            od = dist2(ox, oy, rx, ry)
            key = (od - sd, -sd)  # primary bigger, then smaller sd
            if best is None or key > best_key:
                best = (rx, ry)
                best_key = key
        tx, ty = best
    else:
        # No resources: move to center-ish and avoid obstacles
        tx, ty = w // 2, h // 2

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic tie-break order already fixed above.

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        # Primary: get closer to target
        d_to_target = dist2(nx, ny, tx, ty)

        # Secondary: avoid stepping into opponent's immediate approach (slight)
        opp_step = dist2(nx, ny, ox, oy)
        # If opponent is adjacent to us, prefer staying away
        adj = (abs(ox - sx) <= 1 and abs(oy - sy) <= 1)

        # Tertiary: bias away from obstacles using local occupancy
        obstacle_near = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                px, py = nx + ax, ny + ay
                if inb(px, py) and (px, py) in obstacles:
                    obstacle_near += 1

        score = (-d_to_target, -opp_step, obstacle_near * -0.05, -adj * 0.1)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
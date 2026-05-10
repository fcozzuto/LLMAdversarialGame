def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles") or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    self_role = str(observation.get("self_role") or "")
    is_evader = "evader" in self_role.lower()

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    def dist2(nx, ny):
        dx = nx - ox
        dy = ny - oy
        return dx * dx + dy * dy

    def wall_pen(nx, ny):
        # distance from nearest wall (smaller => closer to wall)
        return min(nx, ny, (w - 1 - nx), (h - 1 - ny))

    best_move = [0, 0]
    best_val = None

    # Novelty change: deterministic "zig-zag" bias that avoids oscillation by preferring moves
    # that change the sign of (dx,dy) projection relative to opponent direction when possible.
    step = observation.get("turn_index", 0)
    phase = 1 if (int(step) % 2 == 0) else -1

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        d = dist2(nx, ny)
        # obstacle-aware micro-bias: prefer moves with fewer blocked neighbors (prevents trapping)
        nb = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if not (0 <= tx < w and 0 <= ty < h) or (tx, ty) in blocked:
                    nb += 1
        wp = wall_pen(nx, ny)

        # projection to encourage "escape lines" vs "catch lines"
        proj_x = (nx - ox) * (sx - ox)
        proj_y = (ny - oy) * (sy - oy)
        proj = proj_x + proj_y

        if is_evader:
            val = (d * 10.0) - (nb * 0.08) - (wp * 0.02)
            # prefer moving that increases projection away from pursuer
            val += (phase * 0.03) * (proj)
        else:
            val = (-d * 10.0) - (nb * 0.08) - (wp * 0.01)
            # prefer reducing projection towards pursuer direction
            val += (-phase * 0.02) * (proj)

        # deterministic tie-break: larger val, then lexicographically smaller [dx,dy] weighted
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]
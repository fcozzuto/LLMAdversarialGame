def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    is_evader = str(observation.get("self_role", "")).lower() == "evader"

    corner_targets = []
    corner_targets.append((0, 0))
    corner_targets.append((w - 1, 0))
    corner_targets.append((0, h - 1))
    corner_targets.append((w - 1, h - 1))

    def nearest_obstacle_rep(x, y):
        if not obs:
            return 0.0
        best = 10**9
        for ex, ey in obs:
            d = abs(x - ex) + abs(y - ey)
            if d < best:
                best = d
        return 1.0 / (1.0 + best)

    def eval_move(nx, ny):
        dxo, dyo = nx - ox, ny - oy
        dist2 = dxo * dxo + dyo * dyo

        # Encourage blocking/pincer behavior vs corner evasion:
        # If opponent is near a corner, steer toward that corner from your side.
        tx, ty = min(corner_targets, key=lambda c: (ox - c[0]) * (ox - c[0]) + (oy - c[1]) * (oy - c[1]))
        tdist2 = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        edge = (nx in (0, w - 1)) or (ny in (0, h - 1))

        rep = nearest_obstacle_rep(nx, ny)

        if is_evader:
            # Maximize distance; avoid obstacles; prefer edges only if it increases distance to opponent corner.
            far = dist2
            corner_bias = -0.15 * tdist2  # keep moving away from the opponent's nearest corner
            edge_bias = 0.05 if edge else -0.03
            return far + corner_bias + edge_bias - 1.2 * rep
        else:
            # Pursuer: minimize distance; also reduce distance to opponent's nearest corner to keep pressure.
            close = -dist2
            approach_corner = -0.10 * tdist2
            edge_bias = 0.04 if edge else 0.0
            return close + approach_corner + edge_bias + 0.6 * rep

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        v = eval_move(nx, ny)
        if best_val is None or v > best_val:
            best_val = v
            best = (dx, dy)
    return [int(best[0]), int(best[1])]
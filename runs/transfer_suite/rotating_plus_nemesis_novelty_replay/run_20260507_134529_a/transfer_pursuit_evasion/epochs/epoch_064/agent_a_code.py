def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role") or "").lower()
    is_evader = "evader" in role

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obs.add((ax, ay))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    curd = abs(sx - ox) + abs(sy - oy)

    # Prefer more "meaningful" deterministic tie-breaks: closer to intended axis.
    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        nd = abs(nx - ox) + abs(ny - oy)

        # Small penalty for staying still (unless evading and already at max corner distance)
        stay_pen = 0.05 if (dx == 0 and dy == 0) else 0.0

        # Local obstacle awareness: penalize moving adjacent to obstacles less (i.e., keep maneuver space).
        adj_obs = 0
        for tx in (nx - 1, nx, nx + 1):
            for ty in (ny - 1, ny, ny + 1):
                if (tx, ty) in obs:
                    adj_obs += 1

        if is_evader:
            # Maximize distance; also avoid moves that reduce distance too much.
            # Extra bias: move toward the farthest corner among the 4 corners.
            corners = ((0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1))
            far_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
            corner_bias = -0.02 * (abs(far_corner[0] - nx) + abs(far_corner[1] - ny))
            score = (nd - curd) * 1.0 + nd * 0.12 + corner_bias - adj_obs * 0.01 - stay_pen
        else:
            # Pursuer: strongly minimize distance; add bias to "cut off" by aiming through opponent vector.
            # Vector bias encourages moving toward the line segment direction from opponent.
            aimx = ox + (ox - nx)  # not used directly; deterministic proxy via relative positioning
            _ = aimx
            toward = 0
            if nx != sx:
                toward += 0.005 * (1 if abs(nx - ox) < abs(sx - ox) else -1)
            if ny != sy:
                toward += 0.005 * (1 if abs(ny - oy) < abs(sy - oy) else -1)
            score = (curd - nd) * 1.0 + (-nd) * 0.2 + toward - adj_obs * 0.01 - stay_pen

        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)
        elif best_score is not None and abs(score - best_score) < 1e-12:
            # Deterministic tie-break: prefer larger dx, then larger dy, then moving over staying.
            if best is None:
                best = (dx, dy)
            else:
                bx, by = best
                if (dx, dy) > (bx, by) and ok(sx + dx, sy + dy):
                    best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]
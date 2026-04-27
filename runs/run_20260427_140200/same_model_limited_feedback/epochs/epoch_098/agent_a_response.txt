def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = {(p[0], p[1]) for p in obstacles}
    dxs = (-1, 0, 1)
    # Candidate next positions
    candidates = []
    for dx in dxs:
        for dy in dxs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set:
                candidates.append((dx, dy, nx, ny))
    if not candidates:
        candidates = [(0, 0, sx, sy)]
    # If resources exist, choose move that maximizes distance advantage to the best contested resource
    if resources:
        best = None
        best_val = -10**9
        for dx, dy, nx, ny in candidates:
            # immediate pickup
            val = 0
            if (nx, ny) in {(r[0], r[1]) for r in resources}:
                val += 1000
            # compute best advantage over all resources
            max_adv = -10**9
            for r in resources:
                rx, ry = r[0], r[1]
                ds = max(abs(nx - rx), abs(ny - ry))
                do = max(abs(ox - rx), abs(oy - ry))
                adv = do - ds  # positive means we are closer than opponent
                if adv > max_adv:
                    max_adv = adv
            val += 50 * max_adv
            # small tiebreakers: stay away from obstacles' immediate neighbors to reduce getting stuck
            # and prefer moving toward center to keep mobility
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            val -= 0.1 * (abs(nx - cx) + abs(ny - cy))
            # Prefer moves that reduce opponent distance to any resource we are targeting
            if max_adv <= 0:
                # still keep deterministic pressure: go to closest resource for us
                dmin = 10**9
                for r in resources:
                    rx, ry = r[0], r[1]
                    dmin = min(dmin, max(abs(nx - rx), abs(ny - ry)))
                val -= dmin
            if val > best_val:
                best_val = val
                best = (dx, dy)
        return [int(best[0]), int(best[1])]
    # No resources: move toward center
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    best_d = 10**9
    for dx, dy, nx, ny in candidates:
        d = abs(nx - cx) + abs(ny - cy)
        if d < best_d:
            best_d = d
            best = (dx, dy)
    return [int(best[0]), int(best[1])]
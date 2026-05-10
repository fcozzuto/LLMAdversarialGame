def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (sx, sy)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obs.add((x, y))
        except Exception:
            pass

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                unclaimed.add((x, y))
        except Exception:
            pass

    cx, cy = (W - 1) / 2.0, (H - 1) / 2.0
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]

    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < W and 0 <= ny < H):
            continue
        if (nx, ny) in obs:
            continue

        # Score: prioritize unclaimed; otherwise move toward center; slight pressure vs opponent.
        if (nx, ny) in unclaimed:
            s = 10**6
        else:
            ddx, ddy = nx - cx, ny - cy
            s = - (ddx * ddx + ddy * ddy)

        # Favor moving away from opponent if targeting unclaimed, else move a bit toward them.
        d_opp = abs(nx - ox) + abs(ny - oy)
        if (nx, ny) in unclaimed:
            s += d_opp
        else:
            s -= d_opp * 0.01

        # Deterministic tie-break: prefer earlier directions order.
        if best is None or s > best_score:
            best_score = s
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best
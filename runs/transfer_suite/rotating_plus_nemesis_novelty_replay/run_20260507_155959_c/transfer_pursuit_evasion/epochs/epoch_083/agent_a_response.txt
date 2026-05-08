def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    self_is_evader = ("evad" in self_role) or ("runner" in self_role) or ("evasion" in self_role) or self_role == "evader"
    # If unsure, assume we are pursuer unless clearly evader.
    pursuer = not self_is_evader
    opp_is_evader = ("evad" in opp_role) or ("runner" in opp_role) or ("evasion" in opp_role) or opp_role == "evader"

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def score_for(nx, ny):
        # Greedy pursuit/evasion with small tie-breakers toward center and along vector.
        dx, dy = ox - nx, oy - ny
        dist = (dx * dx + dy * dy)
        center_bias = -((nx - (w - 1) / 2.0) ** 2 + (ny - (h - 1) / 2.0) ** 2) / (w * h)
        if pursuer:
            # minimize distance; reward also for moving in the general direction to prevent zigzag stalls
            dir_progress = ((nx - sx) * (ox - sx) + (ny - sy) * (oy - sy))
            return -dist + 0.01 * dir_progress + 0.001 * center_bias
        else:
            # maximize distance from opponent; discourage getting too close to edges if possible
            dir_progress = ((nx - sx) * (sx - ox) + (ny - sy) * (sy - oy))
            edge_penalty = ((nx == 0) or (nx == w - 1) or (ny == 0) or (ny == h - 1)) * 0.05
            return dist + 0.01 * dir_progress + 0.001 * center_bias - edge_penalty

    best = None
    best_val = None
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        val = score_for(nx, ny)
        # deterministic tie-break: prefer moves in fixed order already; then smaller dx, then smaller dy
        if best is None or val > best_val + 1e-12 or (abs(val - best_val) <= 1e-12 and (dxm, dym) < best):
            best = (dxm, dym)
            best_val = val

    if best is None:
        return [0, 0]
    return [best[0], best[1]]
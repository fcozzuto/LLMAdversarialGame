def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def clamp(x, lo, hi):
        return lo if x < lo else hi if x > hi else x

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def d2(a, b):
        dx = a[0]-b[0]; dy = a[1]-b[1]
        return dx*dx + dy*dy

    best_res = None
    if resources:
        # Prefer resources that are relatively closer to us than to opponent (material change from simple nearest-self).
        best_score = None
        for rx, ry in resources:
            rs = d2((sx, sy), (rx, ry))
            ro = d2((ox, oy), (rx, ry))
            # Normalize-ish: smaller is better
            val = rs - 0.65 * ro
            if best_score is None or val < best_score or (val == best_score and (rx, ry) < best_res):
                best_score = val
                best_res = (rx, ry)

    target = best_res
    if target is None:
        # No visible resources: move toward center while also drifting away from opponent.
        target = (w//2, h//2)

    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obstacles:
            continue
        # Heuristic: get closer to target; discourage allowing opponent to be closer than us.
        self_to_t = d2((nx, ny), target)
        opp_to_t = d2((ox, oy), target)
        # If we can make ourselves strictly closer than opponent, boost it.
        rel = (opp_to_t - self_to_t)
        # Also prefer increasing distance to opponent to reduce interference.
        dist_opp = d2((nx, ny), (ox, oy))
        # Mild obstacle avoidance (prefer cells not adjacent to obstacles).
        adj = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0: 
                    continue
                px, py = nx + ax, ny + ay
                if (px, py) in obstacles:
                    adj += 1
        val = self_to_t * 1.0 + opp_to_t * 0.02 - 0.9 * rel - 0.08 * dist_opp + 0.3 * adj
        if best_val is None or val < best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
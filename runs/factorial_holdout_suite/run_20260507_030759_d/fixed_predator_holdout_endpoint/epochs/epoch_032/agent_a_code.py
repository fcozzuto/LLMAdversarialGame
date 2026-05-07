def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def md(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)
    def blocked(x, y): return (x, y) in obstacles or not inb(x, y)
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        tx, ty = w // 2, h // 2
        best, bestv = [0, 0], -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if blocked(nx, ny): continue
            v = -md(nx, ny, tx, ty)
            if v > bestv: bestv, best = v, [dx, dy]
        return best

    # Resource_denier response: prefer resources where we have a clear distance edge.
    # If opponent is closer to a resource, penalize it heavily; otherwise reward being closer.
    best_move, best_val = [0, 0], -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny): continue
        local_best = -10**18
        for rx, ry in resources:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            if sd == 0:
                val = 1e9
            else:
                edge = od - sd  # positive if we're closer
                val = edge * 120.0 - sd * 0.6
                if od < sd:  # opponent closer: discourage
                    val -= (sd - od) * 220.0
            # add tiny deterministic bias to break ties by coordinate
            val += (rx * 0.01 + ry * 0.001)
            if val > local_best: local_best = val
        # Encourage reducing opponent's access: if we get closer, prefer it slightly
        opp_now = md(nx, ny, ox, oy)
        local_total = local_best - opp_now * 0.03
        if local_total > best_val:
            best_val, best_move = local_total, [dx, dy]
    return best_move
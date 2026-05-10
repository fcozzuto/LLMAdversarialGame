def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = str(observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in self_role) or ("escape" in self_role) or ("runner" in self_role) or ("flee" in self_role)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    tx, ty = max(corners, key=lambda c: (c[0] - ox) * (c[0] - ox) + (c[1] - oy) * (c[1] - oy)) if is_evader else min(
        corners, key=lambda c: (c[0] - ox) * (c[0] - ox) + (c[1] - oy) * (c[1] - oy)
    )

    def best_move(target_farther):
        deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
        best = None
        best_val = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            d_opp = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            d_t = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
            # Heuristic: evader wants large d_opp; pursuer wants small d_opp. Also prefer moving toward/away from a corner.
            val = (-d_opp, d_t) if target_farther else (d_opp, -d_t)
            if best_val is None or val < best_val:
                best_val = val
                best = (dx, dy)
        return best if best is not None else (0, 0)

    # If near the opponent, evader prioritizes increasing distance; pursuer always closes in.
    cur_d2 = (sx - ox) * (sx - ox) + (sy - oy) * (sy - oy)
    if is_evader:
        # When close, strongly run from opponent; otherwise keep corner-driven escape.
        if cur_d2 <= 9:
            m = best_move(True)
        else:
            m = best_move(True)
    else:
        m = best_move(False)

    dx, dy = m
    return [int(dx), int(dy)]
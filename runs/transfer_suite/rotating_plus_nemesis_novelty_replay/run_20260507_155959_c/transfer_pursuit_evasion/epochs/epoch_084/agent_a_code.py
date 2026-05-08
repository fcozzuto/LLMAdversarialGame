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
    self_evader = ("evad" in self_role) or ("runner" in self_role) or ("evasion" in self_role) or self_role == "evader"
    opp_evader = ("evad" in opp_role) or ("runner" in opp_role) or ("evasion" in opp_role) or opp_role == "evader"

    dir8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def dist2(x, y, tx, ty):
        dx, dy = x - tx, y - ty
        return dx * dx + dy * dy

    tx, ty = ox, oy
    chase = not (self_evader and not opp_evader)
    # If both are evaders, still choose deterministically to avoid getting stuck: chase lightly.
    if self_evader and opp_evader:
        chase = True

    best = None
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    bias_x = int(round(cx - (sx - ox) * 0.0))
    bias_y = int(round(cy - (sy - oy) * 0.0))
    # bias point (center) for tie-breaking
    bx, by = int(round(cx)), int(round(cy))

    for dx, dy in dir8:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = dist2(nx, ny, tx, ty)
        d0 = dist2(sx, sy, tx, ty)
        improve = (d0 - d) if chase else (d - d0)
        center = -dist2(nx, ny, bx, by) * 0.001
        score = improve + center
        if best is None or score > best[0] or (score == best[0] and (dx, dy) < best[1]):
            best = (score, (dx, dy))

    if best is None:
        return [0, 0]
    return [best[1][0], best[1][1]]
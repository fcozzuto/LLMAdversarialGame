def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("pursuer" in role) or ("hunter" in role) or ("seeker" in role)
    is_evader = ("evader" in role) or ("runner" in role) or ("fugitive" in role)
    if not (is_pursuer or is_evader):
        is_pursuer = True
    toward = is_pursuer

    obs = set()
    for b in (observation.get("obstacles") or []):
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    def score_move(nx, ny):
        d = dist2(nx, ny)
        # Primary: move closer/farther; Secondary: prefer center-ish to avoid corner traps.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))
        primary = -d if toward else d
        return primary + 0.001 * center

    best = [0, 0]
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        v = score_move(nx, ny)
        if best_val is None or (v > best_val) or (v == best_val and (dx, dy) < tuple(best)):
            best_val = v
            best = [dx, dy]

    return [int(best[0]), int(best[1])]
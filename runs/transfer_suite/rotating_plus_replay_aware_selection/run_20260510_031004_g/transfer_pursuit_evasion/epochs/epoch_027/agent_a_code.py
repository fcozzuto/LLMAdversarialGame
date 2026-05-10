def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = str(observation.get("self_role", "") or "").lower()
    evader = ("evader" in role) or ("runner" in role) or ("escape" in role)
    pursuer = ("pursuer" in role) or ("chaser" in role)
    if not (evader or pursuer):
        evader = True  # fallback

    obs_set = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def score(nx, ny):
        if (nx, ny) == (ox, oy):
            return 10**9 if pursuer else -10**9
        dx = nx - ox
        dy = ny - oy
        d2 = dx * dx + dy * dy
        # discourage stepping onto obstacles
        if (nx, ny) in obs_set:
            return -10**8
        # tie-breaks: keep away from edges for evader, toward edges for pursuer
        edge_pen = min(nx, w - 1 - nx) + min(ny, h - 1 - ny)
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_d = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
        if evader:
            # maximize distance; prefer higher edge_pen and closer to center a bit (less corner trapping)
            return d2 * 10 + edge_pen - 0.5 * center_d
        else:
            # minimize distance; prefer higher edge_pen to avoid getting boxed by obstacles; slight center bias
            return -d2 * 10 + edge_pen - 0.1 * center_d

    best_move = [0, 0]
    best_val = None
    # deterministic tie-break order: as listed in moves
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h:
            v = score(nx, ny)
            if best_val is None or v > best_val:
                best_val = v
                best_move = [dx, dy]
    return best_move
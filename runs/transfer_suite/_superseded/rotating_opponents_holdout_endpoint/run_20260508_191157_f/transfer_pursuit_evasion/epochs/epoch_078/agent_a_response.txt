def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obst_list = observation.get("obstacles") or []
    obst = set((p[0], p[1]) for p in obst_list)
    role = observation.get("self_role", "pursuer")
    pursuer = (role != "evader")

    def dist2(x, y, a, b):
        dx = x - a
        dy = y - b
        return dx * dx + dy * dy

    # Slightly prefer approaching along the dominant axis to "wall-run" counter evasion.
    def dom_axis_score(nx, ny):
        ax = abs(ox - sx)
        ay = abs(oy - sy)
        if ax >= ay:
            return -abs(ox - nx)  # pursuer: reduce |ox-nx|, evader: increase
        return -abs(oy - ny)

    best = None
    best_key = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obst:
                continue

            d = dist2(nx, ny, ox, oy)
            # Main objective: pursuer minimize distance, evader maximize distance
            main = -d if pursuer else d

            # Counter wall-run: if pursuer, discourage getting too aligned with opponent along walls
            # by also trying to reduce perpendicular distance.
            perp = 0
            if abs(ox - sx) >= abs(oy - sy):
                perp = -abs(oy - ny) if pursuer else abs(oy - ny)
            else:
                perp = -abs(ox - nx) if pursuer else abs(ox - nx)

            # Boundary preference for evader: move toward nearest boundary away from pursuer.
            boundary = 0
            if not pursuer:
                left = nx
                right = (w - 1) - nx
                top = ny
                bottom = (h - 1) - ny
                m = min(left, right, top, bottom)  # closer to boundary is smaller, so invert for evader
                boundary = -m

            # Deterministic tie-break: favor staying closer to center for pursuer; for evader prefer farther.
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            center_d2 = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
            center_term = (-center_d2) if pursuer else (center_d2)

            # Small penalty for staying still (prevents getting stuck).
            still_pen = -0.001 if (dx == 0 and dy == 0) else 0.0

            key = (main, perp, (dom_axis_score(nx, ny)), boundary, center_term, still_pen, dx, dy)
            if best_key is None or key > best_key:
                best_key = key
                best = [dx, dy]

    if best is None:
        return [0, 0]
    return best
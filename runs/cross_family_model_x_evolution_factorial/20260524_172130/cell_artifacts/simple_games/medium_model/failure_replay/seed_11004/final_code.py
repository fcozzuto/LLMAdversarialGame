def choose_move(observation):
    obs = observation or {}
    # Defensive extraction with defaults
    pos = obs.get('self_position', obs.get('position', (0, 0)))
    if isinstance(pos, (list, tuple)) and len(pos) >= 2:
        x, y = pos[0], pos[1]
    else:
        x, y = 0, 0

    def clamp(v):
        if v < -1:
            return -1
        if v > 1:
            return 1
        return 0

    best_dx, best_dy = 0, 0

    # 1) Move away from opponent if known
    opp = obs.get('opponent_position', obs.get('opponent', None))
    if isinstance(opp, (list, tuple)) and len(opp) >= 2:
        ox, oy = opp[0], opp[1]
        dx = clamp(x - ox)
        dy = clamp(y - oy)
        if dx != 0 or dy != 0:
            return [dx, dy]

    # 2) Move toward nearest resource if available
    resources = obs.get('resources', [])
    if isinstance(resources, (list, tuple)) and resources:
        best = None
        bestd = None
        for r in resources:
            if not isinstance(r, (list, tuple)) or len(r) < 2:
                continue
            rx, ry = r[0], r[1]
            d = abs(rx - x) + abs(ry - y)
            if bestd is None or d < bestd:
                bestd = d
                best = (rx, ry)
        if best is not None:
            rx, ry = best
            dx = clamp(rx - x)
            dy = clamp(ry - y)
            if dx != 0 or dy != 0:
                return [dx, dy]

    # 3) If no immediate targets, move toward grid center for balanced exploration
    w = obs.get('grid_width', 0)
    h = obs.get('grid_height', 0)
    if isinstance(w, int) and isinstance(h, int) and w > 0 and h > 0:
        gx, gy = (w // 2, h // 2)
        dx = clamp(gx - x)
        dy = clamp(gy - y)
        if dx != 0 or dy != 0:
            return [dx, dy]

    return [best_dx, best_dy]

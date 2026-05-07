def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    if not resources:
        return [0, 0]

    if (sx, sy) in resources:
        return [0, 0]

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        # Prefer resources we can reach first; otherwise only if race is close.
        if sd <= od:
            lead = od - sd  # larger is better for us
            key = (-lead, sd, rx + 13 * ry)
        else:
            # If opponent much faster, deprioritize heavily.
            gap = sd - od
            key = (gap * 4 + 1, od, sd, rx + 13 * ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]
    tx, ty = best

    # Choose deterministic best step toward target, avoiding stepping into obstacles.
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if (nx, ny) in obstacles:
                continue
            # Primary: reduce distance to target.
            d_to = md(nx, ny, tx, ty)
            # Secondary: don't get boxed; prefer higher "freedom".
            freedom = 0
            for ex in (-1, 0, 1):
                for ey in (-1, 0, 1):
                    px, py = nx + ex, ny + ey
                    if 0 <= px < observation.get("grid_width", 8) and 0 <= py < observation.get("grid_height", 8):
                        if (px, py) not in obstacles:
                            freedom += 1
            # Tertiary: slight bias away from opponent if equally good.
            d_opp = md(nx, ny, ox, oy)
            candidates.append((d_to, -freedom, d_opp, dx, dy))
    candidates.sort()
    return [int(candidates[0][3]), int(candidates[0][4])]
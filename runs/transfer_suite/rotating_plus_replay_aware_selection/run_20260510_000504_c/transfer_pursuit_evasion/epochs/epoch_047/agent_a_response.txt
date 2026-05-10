def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    i_am_pursuer = ("purs" in self_role) or ("chase" in self_role) or ("hunter" in self_role)
    if not i_am_pursuer and (("purs" in opp_role) or ("chase" in opp_role) or ("hunter" in opp_role)):
        i_am_pursuer = False
    if not i_am_pursuer:
        if not (("purs" in opp_role) or ("chase" in opp_role) or ("hunter" in opp_role)):
            i_am_pursuer = True

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def obs_pen(nx, ny):
        p = 0
        for ax, ay in obstacles:
            dx, dy = nx - ax, ny - ay
            d = dx * dx + dy * dy
            if d == 0:
                return 10**9
            if d <= 4:
                p += (5 - d)  # stronger near obstacles
        return p

    # Evader tries to maximize distance and reduce "alignment" with opponent (avoid zigzag traps).
    # Pursuer tries to minimize distance; when tied, moves with least obstacle penalty.
    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        vx, vy = nx - ox, ny - oy
        dist2 = vx * vx + vy * vy

        # Alignment term: prefer breaking direct line-of-sight for evader, and keep for pursuer.
        # (Using cross product magnitude of movement direction towards opponent corner.)
        ax, ay = ox - sx, oy - sy
        align = abs(vx * ay - vy * ax)  # 0 means collinear

        val = 0
        if i_am_pursuer:
            val = dist2 * 1.0 + obs_pen(nx, ny) * 0.5
            # small deterministic tie-break: prefer moves with larger dx, then dy
            key = (val, -dx, -dy)
        else:
            val = -dist2 * 1.0 + obs_pen(nx, ny) * 0.5 - align * 0.05
            # small deterministic tie-break: prefer moves with smaller dx, then dy
            key = (val, dx, -dy)

        if best is None or key < best_val:
            best = [dx, dy]
            best_val = key

    if best is None:
        # Shouldn't happen, but keep valid deterministic fallback.
        return [0, 0]
    return best
def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    resources = [tuple(r) for r in (observation.get("resources") or []) if 0 <= r[0] < w and 0 <= r[1] < h and (r[0], r[1]) not in obstacles]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def clamp_move(nx, ny):
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return True
        return False
    def d2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy
    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        tx = 1 if sx < (w - 1) / 2.0 else -1 if sx > (w - 1) / 2.0 else 0
        ty = 1 if sy < (h - 1) / 2.0 else -1 if sy > (h - 1) / 2.0 else 0
        return [tx, ty]

    # If opponent is adjacent to any resource, prioritize denying their immediate capture.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not clamp_move(nx, ny):
            continue

        # Value components: take resources that we can reach sooner; penalize moving into opponent-first regions.
        val = 0
        # Prefer staying closer to resources when opponent is likely to sweep.
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # big reward for being first, moderate for contesting
            val += (od - sd) * 20
            # extra bias toward nearby pick-ups
            val += (50 - sd) if sd < 7 else 0

        # Denial term: if opponent is close to any resource, discourage our move that lets them keep same best capture
        # by comparing how many resources remain "near" to opponent after our move.
        opp_pressure = 0
        for rx, ry in resources:
            if man(ox, oy, rx, ry) <= 2:
                opp_pressure += 1
        # Penalize moves that don't change anything about our ability to contest those pressures
        # (proxy: how much closer we get to any pressured resource)
        if opp_pressure:
            closest = 10**9
            for rx, ry in resources:
                if man(ox, oy, rx, ry) <= 2:
                    dd = man(nx, ny, rx, ry)
                    if dd < closest: closest = dd
            val -= closest * 8 + opp_pressure * 5

        # Mild symmetry-breaking to avoid ties: head toward center slightly
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        val -= d2(nx, ny, cx, cy) * 0.002

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
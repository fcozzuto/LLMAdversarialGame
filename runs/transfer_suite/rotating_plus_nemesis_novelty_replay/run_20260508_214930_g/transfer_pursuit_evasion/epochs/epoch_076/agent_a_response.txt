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

    obstacles = set()
    for b in (observation.get("obstacles") or []):
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    # For evader, bias toward the corner farthest from the pursuer.
    far_corner = max(corners, key=lambda c: (c[0] - ox) ** 2 + (c[1] - oy) ** 2)

    best_move = [0, 0]
    if toward:
        best_primary = 10**18
        best_secondary = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            d = dist2(nx, ny)
            vx, vy = nx - sx, ny - sy
            # Progress heuristic: move with positive dot toward opponent.
            dot = (nx - sx) * (ox - sx) + (ny - sy) * (oy - sy)
            # Small wall-avoidance: prefer higher clearance if tie.
            clearance = 0
            for ax, ay in deltas:
                tx, ty = nx + ax, ny + ay
                if free(tx, ty):
                    clearance += 1
            primary = d
            secondary = dot * 1000 + clearance
            if primary < best_primary or (primary == best_primary and secondary > best_secondary):
                best_primary, best_secondary = primary, secondary
                best_move = [dx, dy]
    else:
        best_primary = -10**18
        best_secondary = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            d = dist2(nx, ny)
            # Bias toward farthest corner, plus clearance
            corner_dot = (nx - sx) * (far_corner[0] - sx) + (ny - sy) * (far_corner[1] - sy)
            clearance = 0
            for ax, ay in deltas:
                tx, ty = nx + ax, ny + ay
                if free(tx, ty):
                    clearance += 1
            primary = d
            secondary = corner_dot * 1000 + clearance
            if primary > best_primary or (primary == best_primary and secondary > best_secondary):
                best_primary, best_secondary = primary, secondary
                best_move = [dx, dy]

    return best_move
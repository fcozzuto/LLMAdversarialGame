def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    srole = (observation.get("self_role") or "").lower()
    evader = ("evader" in srole) or ("evasion" in srole) or ("runner" in srole)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    # pick corner goal deterministically
    free_corners = [c for c in corners if c not in obst] or corners
    if evader:
        goal = max(free_corners, key=lambda c: (c[0] - ox) ** 2 + (c[1] - oy) ** 2)
    else:
        goal = max(free_corners, key=lambda c: -(((c[0] - ox) ** 2 + (c[1] - oy) ** 2)))  # closest to opponent

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obst:
            continue

        d_op2 = (nx - ox) ** 2 + (ny - oy) ** 2
        d_goal2 = (nx - goal[0]) ** 2 + (ny - goal[1]) ** 2

        if evader:
            # maximize distance from opponent, while also tending to goal corner
            score = d_op2 * 4 + (w * h - d_goal2) * 0.01
            # slight preference for diagonal/forward motion to escape
            score += (1 if dx != 0 and dy != 0 else 0) * 0.001
        else:
            # minimize distance to opponent, while also steering toward goal (corner trap)
            score = -d_op2 * 4 + (w * h - d_goal2) * 0.01
            score += (1 if dx == 0 or dy == 0 else 0) * 0.001  # prefer axial for stability

        if best is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best
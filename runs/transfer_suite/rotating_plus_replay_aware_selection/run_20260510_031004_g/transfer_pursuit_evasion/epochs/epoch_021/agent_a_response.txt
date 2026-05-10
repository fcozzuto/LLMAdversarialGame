def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = str(observation.get("self_role", "") or "").lower()
    evader = "evader" in role

    obs_set = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set

    def dist2(x, y, a=ox, b=oy):
        dx, dy = x - a, y - b
        return dx * dx + dy * dy

    def free_neighbors(x, y):
        c = 0
        for ddx, ddy in deltas:
            if valid(x + ddx, y + ddy):
                c += 1
        return c

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if evader:
        # Prefer the corner that is farthest from pursuer.
        tx, ty = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    else:
        # Prefer the corner that is closest to evader (often where evader tries to head).
        tx, ty = min(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    best = None
    best_sc = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d = dist2(nx, ny)
        fn = free_neighbors(nx, ny)
        man = abs(nx - tx) + abs(ny - ty)

        # Score: evader maximizes distance & mobility while still making progress to target corner.
        # Pursuer minimizes distance and uses mobility to navigate around obstacles.
        if evader:
            sc = (d * 3.0) + (fn * 0.5) - (man * 0.05)
        else:
            sc = (-d * 3.0) + (fn * 0.5) - (man * 0.02)

        if best_sc is None or sc > best_sc:
            best_sc = sc
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best
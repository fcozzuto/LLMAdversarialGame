def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role) or ("fugitive" in role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    turn = int(observation.get("turn_index", 0) or 0)
    axis_pref = 1 if (turn % 2 == 0) else 0  # alternate axis to reduce zigzag

    best_move = (0, 0)
    best_val = -10**18 if is_evader else 10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d = man(nx, ny, ox, oy)
        # slight corner bias for evader; slight block/corner bias for pursuer
        corner = max(corners, key=lambda c: man(nx, ny, c[0], c[1])) if is_evader else min(corners, key=lambda c: man(nx, ny, c[0], c[1]))
        corner_dist = man(nx, ny, corner[0], corner[1])

        # obstacle proximity penalty
        near_obs = 0
        for ox2, oy2 in obstacles:
            if abs(nx - ox2) + abs(ny - oy2) <= 1:
                near_obs += 1

        # anti-zigzag tie-break: prefer moves that align with axis preference
        axis_move = (1 if dx != 0 else 0) if axis_pref == 0 else (1 if dy != 0 else 0)
        stay_pen = 1 if (dx == 0 and dy == 0) else 0

        if is_evader:
            val = d * 100 - corner_dist * 0.3 - near_obs * 2 - stay_pen * 1 + axis_move * 0.05
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
        else:
            val = d * 100 + corner_dist * 0.1 + near_obs * 2 + stay_pen * 1 - axis_move * 0.05
            if val < best_val:
                best_val = val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = str(observation.get("self_role", "") or "").lower()
    opponent_role = str(observation.get("opponent_role", "") or "").lower()
    evader = ("evad" in self_role) or ("escape" in self_role) or ("runner" in self_role) or ("purs" in opponent_role)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    target = max(corners, key=lambda p: md(p[0], p[1], ox, oy))  # best corner to run to
    tx, ty = int(target[0]), int(target[1])

    best = (0, 0)
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        dfo = md(nx, ny, ox, oy)
        dist_to_target = md(nx, ny, tx, ty)

        # obstacle proximity penalty
        near = 0
        for ax, ay in obstacles:
            if abs(ax - nx) <= 1 and abs(ay - ny) <= 1:
                near += 1

        # if we're evader, maximize distance and move toward best corner; if pursuer, minimize distance
        if evader:
            val = (dfo * 10) - (dist_to_target) - (near * 3)
        else:
            val = (-dfo * 10) - (dist_to_target) - (near * 3)

        if best_val is None or val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]
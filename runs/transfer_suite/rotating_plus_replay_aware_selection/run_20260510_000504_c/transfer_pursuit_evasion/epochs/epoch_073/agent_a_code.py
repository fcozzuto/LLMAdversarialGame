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

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in role) or ("escape" in role) or ("runner" in role)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best_move = [0, 0]
    best_val = -10**18 if is_evader else 10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        d = abs(nx - ox) + abs(ny - oy)
        min_obst = 10**9
        for ax, ay in obstacles:
            t = abs(nx - ax) + abs(ny - ay)
            if t < min_obst:
                min_obst = t
        center_bonus = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)) * 1e-3
        avoid_bonus = min_obst * 0.05  # prefer staying away from obstacles
        val = (d + center_bonus + avoid_bonus) if is_evader else (-d + center_bonus + avoid_bonus)
        if is_evader:
            if val > best_val + 1e-12:
                best_val = val
                best_move = [dx, dy]
        else:
            if val < best_val - 1e-12:
                best_val = val
                best_move = [dx, dy]

    return best_move
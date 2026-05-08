def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                oset.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in oset

    cap_r = int(observation.get("capture_radius", 0) or 0)
    self_role = str(observation.get("self_role", "") or "")
    env = str(observation.get("environment_name", "") or "")
    is_evader = ("evader" in self_role.lower()) or ("evader" in env.lower()) or ("evasion" in self_role.lower()) or ("evasion" in env.lower())

    def wall_dist(x, y):
        return min(x, y, (w - 1) - x, (h - 1) - y)

    best = None
    best_sc = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if cap_r == 0 and nx == ox and ny == oy:
                if is_evader:
                    continue
            dist = abs(nx - ox) + abs(ny - oy)

            # Evader: maximize distance, but prefer staying away from walls/obstacles corners.
            # Pursuer: minimize distance, avoid pushing into walls/corners that may stall.
            if is_evader:
                sc = dist * 10 + wall_dist(nx, ny) - 2 * ((nx == 0 or nx == w - 1) + (ny == 0 or ny == h - 1))
            else:
                sc = -(dist * 10) + wall_dist(nx, ny) - 2 * ((nx == 0 or nx == w - 1) + (ny == 0 or ny == h - 1))
            if best_sc is None or sc > best_sc:
                best_sc = sc
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]
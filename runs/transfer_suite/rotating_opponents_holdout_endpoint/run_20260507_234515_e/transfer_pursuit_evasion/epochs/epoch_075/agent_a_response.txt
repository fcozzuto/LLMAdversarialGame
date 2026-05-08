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
    opp_role = str(observation.get("opponent_role", "") or "")
    env = str(observation.get("environment_name", "") or "")
    is_evader = ("evader" in self_role.lower()) or ("evasion" in self_role.lower()) or ("evader" in env.lower()) or ("evasion" in env.lower())
    is_pursuer = not is_evader

    def manh(x, y, a, b):
        return abs(x - a) + abs(y - b)

    def wall_dist(x, y):
        return min(x, y, (w - 1) - x, (h - 1) - y)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_sc = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        d = manh(nx, ny, ox, oy)
        wall = wall_dist(nx, ny)
        # Obstacle proximity penalty: discourage moving adjacent to obstacles
        near_obs = 0
        for ax, ay in ((nx - 1, ny), (nx + 1, ny), (nx, ny - 1), (nx, ny + 1), (nx - 1, ny - 1), (nx - 1, ny + 1), (nx + 1, ny - 1), (nx + 1, ny + 1)):
            if 0 <= ax < w and 0 <= ay < h and (ax, ay) in oset:
                near_obs += 1

        if cap_r == 0 and nx == ox and ny == oy:
            if is_evader:
                sc = -10**6  # avoid capture
            else:
                sc = 10**6   # capture immediately
        else:
            if is_pursuer:
                # Greedy pursuit: minimize distance; slight preference for tighter walls if tied
                sc = -d * 100 + wall * 2 - near_obs * 5
            else:
                # Evasion: maximize distance; prefer corners (wall distance) and avoid obstacles
                sc = d * 100 + wall * 3 - near_obs * 8

        if best_sc is None or sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]
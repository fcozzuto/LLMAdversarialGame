def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    role = str(observation.get("self_role", "")).lower()
    is_evader = (role == "evader")

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(x, y, a, b):
        dx, dy = x - a, y - b
        return dx * dx + dy * dy

    def obst_pen(x, y):
        # heavy avoid for standing on/adjacent obstacles; light for near
        p = 0
        for ax, ay in obs:
            d = abs(x - ax) + abs(y - ay)
            if d == 0:
                return 10**9
            if d == 1:
                p += 8
            elif d == 2:
                p += 2
        return p

    best_dx, best_dy = 0, 0
    if is_evader:
        best_val = -10**18
    else:
        best_val = 10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        d = dist2(nx, ny, ox, oy)
        pen = obst_pen(nx, ny)

        # small tie-break: prefer staying away/towards corners consistently
        corner_bias = (nx if dx != 0 else 0) + (ny if dy != 0 else 0)
        if is_evader:
            val = d - pen + 0.001 * corner_bias
            if val > best_val:
                best_val = val
                best_dx, best_dy = dx, dy
        else:
            val = d + 2.0 * pen - 0.001 * corner_bias
            if val < best_val:
                best_val = val
                best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]
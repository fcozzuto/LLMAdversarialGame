def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        try:
            x, y = p
            obs.add((int(x), int(y)))
        except:
            pass

    sr = str(observation.get("self_role", "")).lower()
    i_am_evader = ("evad" in sr) or ("escape" in sr) or ("runner" in sr)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def clamp_in(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def near_obstacle_penalty(x, y):
        if not obs:
            return 0.0
        if (x, y) in obs:
            return 1e9
        m = 10.0
        for bx, by in obs:
            d = abs(x - bx) + abs(y - by)
            if d == 0:
                return 1e9
            if d < m:
                m = d
        return 2.5 / m

    def edge_penalty(x, y):
        # Prevent getting stuck by immediately backing into walls too long.
        return (0 if 1 <= x <= w - 2 else 0.15) + (0 if 1 <= y <= h - 2 else 0.15)

    best = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not clamp_in(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        d = dist2(nx, ny, ox, oy)
        p = near_obstacle_penalty(nx, ny) + edge_penalty(nx, ny)
        # If evader: maximize distance (with obstacle avoidance).
        # If pursuer: minimize distance (with obstacle avoidance).
        score = (d - 30.0 * p) if i_am_evader else (-d - 30.0 * p)
        if best is None or score > best_score:
            best_score = score
            best = [dx, dy]

    return best if best is not None else [0, 0]
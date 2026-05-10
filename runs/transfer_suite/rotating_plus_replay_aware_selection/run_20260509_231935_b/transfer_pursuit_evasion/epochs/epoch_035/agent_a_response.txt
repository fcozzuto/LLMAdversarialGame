def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = p
            obs.add((int(x), int(y)))

    sr = str(observation.get("self_role", "")).lower()
    is_evader = ("evad" in sr)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def obst_penalty(x, y):
        if (x, y) in obs:
            return 10**9
        p = 0
        for bx, by in obs:
            d = abs(x - bx) + abs(y - by)
            if d == 0:
                return 10**9
            if d == 1:
                p += 4
            elif d == 2:
                p += 2
        return p

    best_move = [0, 0]
    best_score = -10**18 if is_evader else 10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        pen = obst_penalty(nx, ny)
        if pen >= 10**8:
            continue
        d = dist2(nx, ny, ox, oy)
        turn = int(observation.get("turn_index", 0) or 0)
        # Zigzag-friendly: bias to match parity so we don't "shadow" opponent movement.
        parity_bias = 0
        if ((nx + ny + turn) & 1) == 0:
            parity_bias = 1
        if is_evader:
            score = d - 6 * pen + parity_bias
            if score > best_score:
                best_score, best_move = score, [dx, dy]
        else:
            score = d + 6 * pen - parity_bias
            if score < best_score:
                best_score, best_move = score, [dx, dy]

    return best_move
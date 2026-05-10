def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role) or ("flee" in role)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    if (sx, sy) == (ox, oy):
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x, y):
        ax = abs(ox - x)
        ay = abs(oy - y)
        return ax if ax >= ay else ay

    def min_obs_dist(x, y):
        if not obstacles:
            return 10**6
        dmin = 10**9
        for px, py in obstacles:
            d = abs(px - x) + abs(py - y)
            if d < dmin:
                dmin = d
                if dmin == 0:
                    break
        return dmin

    best = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d = cheb(nx, ny)
        md = min_obs_dist(nx, ny)
        # pursuer: minimize distance; evader: maximize distance.
        # extra preference: avoid standing adjacent to obstacles (for both roles).
        avoid = 0
        if md == 0:
            avoid = 1e9
        elif md == 1:
            avoid = 8
        elif md == 2:
            avoid = 3
        else:
            avoid = 0
        score = (-d if not is_evader else d) - avoid
        if best is None or score > best:
            best = score
            best_move = [dx, dy]

    return best_move
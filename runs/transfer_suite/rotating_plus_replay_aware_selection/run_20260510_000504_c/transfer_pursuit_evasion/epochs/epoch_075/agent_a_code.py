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
    is_evader = ("evad" in self_role) or ("escape" in self_role) or ("runner" in self_role)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def nearest_obst_dist(x, y):
        if not obstacles:
            return 99
        dmin = 99
        for a, b in obstacles:
            d = abs(x - a) + abs(y - b)
            if d < dmin:
                dmin = d
                if dmin == 0:
                    return 0
        return dmin

    def dist_to_opp(x, y):
        return abs(x - ox) + abs(y - oy)

    best_move = (0, 0)
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        dopp = dist_to_opp(nx, ny)
        dob = nearest_obst_dist(nx, ny)
        # obstacle proximity penalty; farther obstacles preferred
        obst_term = float(dob)
        # encourage moving away from obstacles; if very close, discourage strongly
        if dob <= 1:
            obst_term -= 4.0
        score = (dopp + 0.25 * obst_term) if is_evader else (-dopp + 0.25 * obst_term)
        if best_score is None:
            best_score = score
            best_move = (dx, dy)
        else:
            if (is_evader and score > best_score) or ((not is_evader) and score > best_score):
                best_score = score
                best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]
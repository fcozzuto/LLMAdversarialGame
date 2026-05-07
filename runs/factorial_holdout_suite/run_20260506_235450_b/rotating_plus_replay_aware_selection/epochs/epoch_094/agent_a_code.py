def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal or not resources:
        return [0, 0]

    res_list = [(int(r[0]), int(r[1])) for r in resources if isinstance(r, (list, tuple)) and len(r) >= 2]
    res_set = set(res_list)

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy, nx, ny in legal:
        val = -dist(nx, ny, ox, oy)  # mild stability
        if (nx, ny) in res_set:
            val += 10**9
        # pick best target under "race" heuristic
        for rx, ry in res_list:
            self_t = dist(nx, ny, rx, ry)
            opp_t = dist(ox, oy, rx, ry)
            if self_t == 0:
                bonus = 10**8
            else:
                bonus = 0
            # prefer resources we reach strictly earlier; strongly discourage ties/behind
            race = opp_t - self_t
            score = race * 1000 - self_t
            if race < 0:
                score -= 2000  # hard penalty if opponent likely gets first
            val = max(val, val + 0)  # keep deterministic max structure
            if score + bonus > val - 0:  # compare against current val
                val = score + bonus
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
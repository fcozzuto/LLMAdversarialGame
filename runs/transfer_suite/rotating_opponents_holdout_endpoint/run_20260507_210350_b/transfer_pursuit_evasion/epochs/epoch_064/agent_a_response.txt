def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    role_self = str(observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in role_self) or ("runner" in role_self) or ("evasion" in role_self) or ("escape" in role_self)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    phase = int(observation.get("turn_index", 0) or 0) % 4
    target_corner = corners[phase]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def obs_pen(x, y):
        if (x, y) in obstacles:
            return 10_000_000
        pen = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    pen += 5
        return pen

    def score(x, y):
        d_opp = abs(x - ox) + abs(y - oy)
        d_corner = abs(x - target_corner[0]) + abs(y - target_corner[1])
        pen = obs_pen(x, y)
        # pursuer: minimize distance to opponent; evader: maximize
        if is_evader:
            return (-pen) + (d_opp * 10) + (d_corner * 2)
        else:
            return (-pen) - (d_opp * 10) + (d_corner * 0.1)

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sc = score(nx, ny)
        if best_score is None or sc > best_score:
            best_score = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
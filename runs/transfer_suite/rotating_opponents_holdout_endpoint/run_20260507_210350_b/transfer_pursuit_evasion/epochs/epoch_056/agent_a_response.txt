def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obs_list = observation.get("obstacles", []) or []
    obstacles = set((int(p[0]), int(p[1])) for p in obs_list if p and len(p) >= 2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    role_self = str(observation.get("self_role", "") or "").lower()
    self_is_evader = ("evader" in role_self) or ("runner" in role_self)
    resources = observation.get("resources", []) or []
    res_set = set((int(p[0]), int(p[1])) for p in resources if p and len(p) >= 2)

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    def obs_penalty(x, y):
        # Encourage positions that are not adjacent to obstacles too much (avoid dead-ends),
        # but keep it small so pursuit/escape dominates.
        p = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in obstacles:
                    p += 1
        return p

    best_move = [0, 0]
    best_val = None

    for dx, dy in moves:
        nx, ny = int(sx + dx), int(sy + dy)
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        d2 = dist2(nx, ny, int(ox), int(oy))
        p = obs_penalty(nx, ny)
        res_bonus = 0
        if (nx, ny) in res_set:
            res_bonus = 3  # small deterministic nudge if resources exist

        # If evader: maximize distance; if pursuer: minimize distance.
        if self_is_evader:
            val = d2 - 0.15 * p + res_bonus
        else:
            val = -d2 - 0.05 * p + res_bonus

        if best_val is None:
            best_val = val
            best_move = [dx, dy]
        else:
            if val > best_val:
                best_val = val
                best_move = [dx, dy]
            elif val == best_val:
                # Deterministic tie-break: prefer moves with smaller |dx| then smaller |dy|
                if (abs(dx), abs(dy)) < (abs(best_move[0]), abs(best_move[1])):
                    best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]
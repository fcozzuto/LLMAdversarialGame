def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    actions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    obs = set()
    for b in observation.get("obstacles", []) or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            try:
                obs.add((int(b[0]), int(b[1])))
            except:
                pass

    role = (observation.get("self_role", "") or "").lower()
    pursuer = ("purs" in role) or ("chase" in role) or ("hunter" in role)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (x, y) in obs
    def valid(x, y): return inb(x, y) and not blocked(x, y)
    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def free_neighbors(x, y):
        c = 0
        for dx, dy in actions:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                c += 1
        return c

    obstacle_list = list(obs)
    best_move = (0, 0)
    best_val = None

    for dx, dy in actions:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0

        if pursuer and nx == ox and ny == oy:
            return [dx, dy]

        d = dist2(nx, ny, ox, oy)
        f = free_neighbors(nx, ny)
        wall_bonus = 0
        if obstacle_list:
            for bx, by in obstacle_list:
                if nx == bx or ny == by:
                    wall_bonus = 2
                    break

        # If pursuing: minimize distance, prefer having options; avoid becoming trapped
        if pursuer:
            val = -d + 0.35 * f + 0.15 * wall_bonus
        # If evading: maximize distance, prefer preserving mobility and "wall-running" alignment
        else:
            val = d + 0.45 * f + 0.25 * wall_bonus
            if nx == ox and ny == oy:
                val -= 100000

        if best_val is None or (val > best_val if not pursuer else val > best_val):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
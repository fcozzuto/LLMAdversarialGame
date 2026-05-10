def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    role = str(observation.get("self_role", "")).lower()
    opp_role = str(observation.get("opponent_role", "")).lower()

    evader_keys = ("evader", "evade", "escape", "runner", "evasion")
    i_am_evader = any(k in role for k in evader_keys) and not any(k in opp_role for k in evader_keys)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (x, y) in obstacles

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def free_neighbors(x, y):
        c = 0
        for dx, dy in moves:
            if dx == 0 and dy == 0:
                continue
            x2, y2 = x + dx, y + dy
            if inb(x2, y2) and not blocked(x2, y2):
                c += 1
        return c

    # Simple heuristic: pursue/minimize distance; evade/maximize distance, with safety bias.
    best = None
    best_sc = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            sc = -10**9 if not i_am_evader else -10**9
        else:
            d = abs(nx - ox) + abs(ny - oy)
            safety = free_neighbors(nx, ny)
            # slight bias to keep moving along diagonal when useful
            diag_bonus = 0.1 if dx != 0 and dy != 0 else 0.0
            if i_am_evader:
                sc = d + 0.6 * safety + diag_bonus
            else:
                sc = -d + 0.6 * safety + diag_bonus
        if best is None or sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    return [int(best[0]), int(best[1])]
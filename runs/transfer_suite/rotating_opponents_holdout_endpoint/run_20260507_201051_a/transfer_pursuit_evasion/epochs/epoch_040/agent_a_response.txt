def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = str(observation.get("self_role", "")).lower()
    opponent_role = str(observation.get("opponent_role", "")).lower()
    i_am_evader = ("evader" in self_role) or ("pursuer" in opponent_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    def obstacle_pressure(x, y):
        cnt = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                nx, ny = x + ddx, y + ddy
                if not inb(nx, ny) or (nx, ny) in obs:
                    cnt += 1
        return cnt

    best_move = [0, 0]
    best_val = None
    # Small deterministic preference to avoid ties: prioritize moves that change x first, then y.
    tie_pref = {(dx, dy): (abs(dx) == 1, abs(dy) == 1, dx, dy) for dx, dy in moves}

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d = dist2(nx, ny)
        press = obstacle_pressure(nx, ny)
        # Evader: maximize distance, minimize being boxed in.
        # Pursuer: minimize distance, avoid boxed-in self positions.
        val = d - 0.6 * press if i_am_evader else -d - 0.6 * press
        if best_val is None:
            best_val = val
            best_move = [dx, dy]
        else:
            if val > best_val + 1e-9:
                best_val = val
                best_move = [dx, dy]
            elif abs(val - best_val) <= 1e-9:
                # Deterministic tie-break
                bp = tie_pref[(best_move[0], best_move[1])]
                cp = tie_pref[(dx, dy)]
                if cp > bp:
                    best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]
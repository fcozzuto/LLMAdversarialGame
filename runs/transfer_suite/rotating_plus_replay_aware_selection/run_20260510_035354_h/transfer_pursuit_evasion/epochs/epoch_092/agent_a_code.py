def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    is_pursuer = ("pursuer" in role) or ("pursuit" in role) or (role == "pursuer")
    is_evader = ("evader" in role) or ("evade" in role) or (role == "evader")

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x, y):
        dx = x - ox
        dy = y - oy
        return dx * dx + dy * dy

    best = None
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            val = -10**18 if is_evader else 10**18
        else:
            d2 = dist2(nx, ny)
            if is_pursuer:
                val = -d2
                if dx != 0 and dy != 0:
                    val += 0.001
            elif is_evader:
                val = d2
                if dx == 0 or dy == 0:
                    val += 0.0005
            else:
                # Unknown role: default to pursuit-like scoring
                val = -d2
                if dx != 0 and dy != 0:
                    val += 0.001

        if best_val is None or val > best_val:
            best_val = val
            best = [dx, dy]

    return best if best is not None else [0, 0]
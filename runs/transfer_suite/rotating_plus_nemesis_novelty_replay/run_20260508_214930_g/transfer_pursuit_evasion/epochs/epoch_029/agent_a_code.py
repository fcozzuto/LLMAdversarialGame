def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    self_pursuer = ("pursuer" in self_role) or ("pursue" in self_role)
    opp_pursuer = ("pursuer" in opp_role) or ("pursue" in opp_role)
    we_pursue = self_pursuer or (opp_pursuer and not self_pursuer)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for b in obstacles:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            obs.add((int(b[0]), int(b[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist_manh(x, y, a, b):
        return abs(x - a) + abs(y - b)

    def obstacle_proximity_penalty(x, y):
        # Strongly penalize stepping into/adjacent to obstacles; still allows movement but avoids collisions.
        p = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in obs:
                    p += 6
        if (x, y) in obs:
            p += 50
        return p

    best = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            val = -10**9
        else:
            dpo = dist_manh(nx, ny, ox, oy)
            # kiting/approach
            val = (dpo if not we_pursue else -dpo) * 3
            val -= obstacle_proximity_penalty(nx, ny)
            # encourage staying away from the map edges if evading (more escape space)
            edge = (nx == 0 or ny == 0 or nx == w - 1 or ny == h - 1)
            if not we_pursue and edge:
                val -= 2
            # when pursuing, prefer moves that reduce distance and don't get stuck against edges
            if we_pursue and edge:
                val -= 1
        if best_val is None or val > best_val:
            best_val = val
            best = (dx, dy)
    return [int(best[0]), int(best[1])]
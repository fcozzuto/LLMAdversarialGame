def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = map(int, observation.get("self_position") or [0, 0])
    ox, oy = map(int, observation.get("opponent_position") or [0, 0])

    obstacles = set()
    for it in observation.get("obstacles") or []:
        try:
            if isinstance(it, dict):
                x, y = it.get("x"), it.get("y")
            else:
                x, y = it[0], it[1]
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    i_am_evader = ("evader" in self_role) or ("pursuer" in self_role and "evader" in opp_role)

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    def dist2(a, b, c, d):
        dx, dy = a - c, b - d
        return dx * dx + dy * dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def step_score(nx, ny):
        # Favor separating/capturing while accounting for obstacle "tightness"
        d_opp = dist2(nx, ny, ox, oy)

        # Nearest-corner objective to encourage/avoid cornering
        c = min(corners, key=lambda k: dist2(ox, oy, k[0], k[1]))
        corner_d = dist2(nx, ny, c[0], c[1])
        # Obstacle crowding penalty: discourage moving into low-mobility cells
        neigh = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if legal(nx + dx, ny + dy):
                    neigh += 1
        tight_pen = (8 - neigh)  # 0..8

        if i_am_evader:
            # Evader: increase distance from pursuer, and head toward a corner (but avoid tight traps)
            return (d_opp * 10) - (corner_d * 0.2) - (tight_pen * 1.5)
        else:
            # Pursuer: decrease distance to evader, while steering toward the evader's nearest corner
            return (-d_opp * 10) - (corner_d * 0.8) - (tight_pen * 0.3)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        v = step_score(nx, ny)
        if best_val is None or v > best_val:
            best_val = v
            best_move = (dx, dy)
        elif v == best_val:
            # Deterministic tie-break: prefer moving (not staying), then lexicographic
            if best_move == (0, 0) and (dx, dy) != (0, 0):
                best_move = (dx, dy)
            elif (dx, dy) < best_move:
                best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]
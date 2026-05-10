def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    self_role = (observation.get("self_role") or "").lower()

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0:
            ax = -ax
        ay = y1 - y2
        if ay < 0:
            ay = -ay
        return ax if ax > ay else ay

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def best_resource(for_pursuer):
        if not resources:
            return None
        rx, ry = sx, sy
        best = None
        for r in resources:
            rxi, ryi = r
            d = cheb(sx, sy, rxi, ryi)
            key = (-d, rxi, ryi) if (not for_pursuer) else (d, rxi, ryi)
            if best is None or key < best[0]:
                best = (key, (rxi, ryi))
        return best[1]

    evader = ("evader" in self_role) and ("pursuer" not in self_role)
    pursuer = ("pursuer" in self_role) and not evader

    target = best_resource(pursuer) if resources else None

    best_move = [0, 0]
    best_val = -10**18 if not evader else -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist = cheb(nx, ny, ox, oy)
        if nx == ox and ny == oy:
            val = 10.0 if pursuer else -10.0
        else:
            if pursuer:
                val = -dist * 10.0
                if target is not None:
                    val -= cheb(nx, ny, target[0], target[1])
            else:  # evader or default
                val = dist * 10.0
                if target is not None:
                    val += cheb(nx, ny, target[0], target[1])
            # small tie-break toward higher y then x for determinism
            val += (ny * 0.001 + nx * 0.000001)
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move
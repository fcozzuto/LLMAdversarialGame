def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role") or "").lower()
    self_is_evader = ("evader" in role) or ("evader" in (observation.get("self_name") or "").lower())

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def clamp_move(x, y, dx, dy):
        nx, ny = x + dx, y + dy
        if ok(nx, ny):
            return nx, ny
        return x, y

    def cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    # One-step minimax: if we're evader, we maximize distance vs opponent greedily minimizing it.
    # If we're pursuer, we minimize distance vs opponent greedily maximizing it.
    best_move = (0, 0)
    best_val = None
    target_sign = 1 if self_is_evader else -1

    if self_is_evader:
        for dx, dy in moves:
            nsx, nsy = clamp_move(sx, sy, dx, dy)
            # opponent (pursuer) best response: reduce distance to us
            best_op_dist = None
            for odx, ody in moves:
                nox, noy = clamp_move(ox, oy, odx, ody)
                dist = cheb((nox, noy), (nsx, nsy))
                if best_op_dist is None or dist < best_op_dist:
                    best_op_dist = dist
                    if best_op_dist == 0:
                        break
            # if capture after opponent move => very bad
            val = (-10**6 if best_op_dist == 0 else best_op_dist) + (nsx + nsy) * 1e-4
            if best_val is None or val > best_val:
                best_val = val
                best_move = (dx, dy)
    else:
        for dx, dy in moves:
            nsx, nsy = clamp_move(sx, sy, dx, dy)
            # opponent (evader) best response: increase distance from us
            best_op_dist = None
            for odx, ody in moves:
                nox, noy = clamp_move(ox, oy, odx, ody)
                dist = cheb((nox, noy), (nsx, nsy))
                if best_op_dist is None or dist > best_op_dist:
                    best_op_dist = dist
            # if we capture immediately => very good
            val = (10**6 if best_op_dist == 0 else -best_op_dist) + (-(nsx + nsy)) * 1e-4
            if best_val is None or val > best_val:
                best_val = val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
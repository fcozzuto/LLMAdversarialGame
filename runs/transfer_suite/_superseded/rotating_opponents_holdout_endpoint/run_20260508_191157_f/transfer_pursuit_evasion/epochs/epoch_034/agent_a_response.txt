def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs_set = {(p[0], p[1]) for p in obstacles}
    role = observation.get("self_role", "pursuer")
    cap = observation.get("capture_radius", 0) or 0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    # Prefer staying legal and not too close to obstacles (both roles)
    def obs_prox(nx, ny):
        if not obstacles:
            return 0
        md = 10**9
        for (ax, ay) in obstacles:
            d = abs(ax - nx) + abs(ay - ny)
            if d < md:
                md = d
                if md <= 1:
                    break
        return md

    if role == "pursuer":
        # Chase opponent, but bias slightly toward the closest corner to restrict escape.
        target_corner = min(corners, key=lambda c: dist((ox, oy), c))
        best_sc = -10**18
        best_mv = (0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs_set:
                continue
            d_op = dist((nx, ny), (ox, oy))
            d_corner = dist((nx, ny), target_corner)
            # capture if within radius (capture_radius likely 0)
            sc = -d_op * 50 - d_corner
            sc += obs_prox(nx, ny) * 2
            if cap == 0 and d_op == 0:
                sc += 10**9
            if sc > best_sc:
                best_sc = sc
                best_mv = (dx, dy)
        return [int(best_mv[0]), int(best_mv[1])]
    else:
        # Evader: maximize distance to pursuer; also steer toward farthest corner.
        target_corner = max(corners, key=lambda c: dist((ox, oy), c))
        best_sc = -10**18
        best_mv = (0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs_set:
                continue
            d_op = dist((nx, ny), (ox, oy))
            d_corner = dist((nx, ny), target_corner)
            sc = d_op * 55 - d_corner * 2
            # avoid obstacle-adjacent moves; also discourage moving closer to any obstacle
            sc += obs_prox(nx, ny) * 6
            if cap == 0 and d_op == 0:
                sc -= 10**9
            if sc > best_sc:
                best_sc = sc
                best_mv = (dx, dy)
        return [int(best_mv[0]), int(best_mv[1])]
def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        try:
            x, y = p
            obs.add((int(x), int(y)))
        except:
            pass

    sr = str(observation.get("self_role", "")).lower()
    is_evader = ("evad" in sr)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def obst_penalty(x, y):
        if (x, y) in obs:
            return 10**9
        # soft penalty near obstacles to avoid getting boxed in
        p = 0
        for bx, by in obs:
            md = abs(x - bx) + abs(y - by)
            if md == 0:
                return 10**9
            if md <= 2:
                p += (3 - md) * 50
        return p

    # If evader, head toward farthest corner from pursuer; if pursuer, head to nearest corner then intercept directly.
    far_corner = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
    near_corner = min(corners, key=lambda c: dist2(c[0], c[1], ox, oy))

    target_x, target_y = (far_corner if is_evader else near_corner)

    best_move = (0, 0)
    best_val = -10**18 if is_evader else 10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        pen = obst_penalty(nx, ny)
        if pen >= 10**8:
            continue
        d_opp = dist2(nx, ny, ox, oy)
        d_tgt = dist2(nx, ny, target_x, target_y)
        # deterministic tie-break: fixed ordering of deltas already
        if is_evader:
            val = d_opp * 10 + d_tgt - pen
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
        else:
            # as pursuer, minimize distance to evader; slight bias toward target corner to control space
            val = -d_opp * 10 - d_tgt - pen
            if val > best_val:
                best_val = val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
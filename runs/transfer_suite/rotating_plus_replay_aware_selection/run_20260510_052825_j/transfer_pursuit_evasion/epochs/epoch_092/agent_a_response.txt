def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    evader = ("evader" in role) or ("escape" in role) or ("runner" in role)

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def free(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx*dx + dy*dy

    # Simple deterministic local scoring with obstacle avoidance and corner preference.
    corners = [(0,0),(0,h-1),(w-1,0),(w-1,h-1)]
    far_corner = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
    near_corner = min(corners, key=lambda c: dist2(c[0], c[1], ox, oy))

    best = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        d_opp = dist2(nx, ny, ox, oy)
        # obstacle proximity penalty (closer obstacles worse)
        md2 = 10**12
        for bx, by in blocked:
            v = dist2(nx, ny, bx, by)
            if v < md2:
                md2 = v
        obs_pen = 0.0 if not blocked else (0.0 if md2 > 9 else (9 - md2) * 0.5)

        # Corner shaping: evader wants far from opponent; pursuer wants near.
        if evader:
            corner_term = -dist2(nx, ny, far_corner[0], far_corner[1])
            score = d_opp + 0.7 * corner_term - 1.2 * obs_pen
        else:
            corner_term = -dist2(nx, ny, near_corner[0], near_corner[1])
            # also prefer moves that don't increase the distance to opponent too much
            score = -d_opp + 0.35 * corner_term - 1.2 * obs_pen

        if best is None or (score > best_score if evader else score > best_score):
            best = [dx, dy]
            best_score = score

    if best is None:
        return [0, 0]
    return best
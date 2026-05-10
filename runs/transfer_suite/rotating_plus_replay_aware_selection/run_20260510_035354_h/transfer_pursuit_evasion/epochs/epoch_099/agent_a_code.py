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

    self_role = str(observation.get("self_role") or "")
    opp_role = str(observation.get("opponent_role") or "")
    s = (self_role + " " + opp_role).lower()
    pursuer = ("pursuer" in self_role.lower()) or ("pursuer" in s and "evader" not in self_role.lower())

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    best_mv = [0, 0]
    best_sc = -10**18 if pursuer else 10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        dist = abs(nx - ox) + abs(ny - oy)
        center_dist = abs(nx - cx) + abs(ny - cy)

        # Pursuer: strictly chase; tie-break to reduce evasion zigzags near center.
        if pursuer:
            sc = -dist * 1000 - center_dist  # smaller center_dist is better (more central)
        else:
            # Evader: maximize distance; prefer staying away from center (evade into corners).
            sc = dist * 1000 + center_dist

        if pursuer:
            if sc > best_sc:
                best_sc = sc
                best_mv = [nx - sx, ny - sy]
        else:
            if sc < best_sc:
                best_sc = sc
                best_mv = [nx - sx, ny - sy]

    # Ensure dx/dy are valid ints in {-1,0,1}
    dx, dy = int(best_mv[0]), int(best_mv[1])
    if dx < -1: dx = -1
    if dx > 1: dx = 1
    if dy < -1: dy = -1
    if dy > 1: dy = 1
    return [dx, dy]
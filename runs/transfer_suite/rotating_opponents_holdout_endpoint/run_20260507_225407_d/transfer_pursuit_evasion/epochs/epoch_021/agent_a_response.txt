def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    role = observation.get("self_role") or "pursuer"

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is None:
            continue
        obstacles.add((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inside(x, y) and (x, y) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    # Likely evader aim: corner farthest from pursuer (us), so pursuer tries to go there.
    far_corner = max(corners, key=lambda c: dist2(sx, sy, c[0], c[1]))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    # If we're very close, still deterministically decide: pursuer closes, evader maximizes distance.
    if role.lower() == "evader":
        # Evade: maximize distance from pursuer, with bias toward far_corner.
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d_opp = dist2(nx, ny, ox, oy)
            d_corner = dist2(nx, ny, far_corner[0], far_corner[1])
            score = (d_opp * 10) + (-d_corner)
            if best is None or score > best[0]:
                best = (score, dx, dy)
    else:
        # Pursuer: if unobstructed, head to far_corner first (cut off), else greedy chase.
        # Blend based on whether far_corner is still meaningfully far.
        pursue_corner = dist2(sx, sy, far_corner[0], far_corner[1]) > 9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            if pursue_corner:
                d_t = dist2(nx, ny, far_corner[0], far_corner[1])
                # Secondary tie-break: also reduce opponent distance to avoid being baited.
                score = (-d_t * 5) + (-dist2(nx, ny, ox, oy))
            else:
                score = (-dist2(nx, ny, ox, oy)) + (-dist2(nx, ny, far_corner[0], far_corner[1]) * 0.2)
            if best is None or score > best[0]:
                best = (score, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]
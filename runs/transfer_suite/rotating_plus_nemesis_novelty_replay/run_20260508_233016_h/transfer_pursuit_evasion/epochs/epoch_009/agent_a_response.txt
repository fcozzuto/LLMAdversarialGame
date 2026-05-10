def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obs = observation.get("obstacles", []) or []
    blocked = set()
    for p in obs:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    pursuer = ("purs" in self_role) or ("evad" in opp_role and "evad" not in self_role)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def man(x, y):
        return abs(x - ox) + abs(y - oy)
    def wall_pen(x, y):
        return min(x, w - 1 - x) + min(y, h - 1 - y)

    # If pursuer: prefer decreasing distance; if close, bias toward "cut-off" positions.
    # If evader: prefer increasing distance; if close, bias toward corner away from pursuer.
    close = man(sx, sy) <= 3
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        d = man(nx, ny)
        wp = wall_pen(nx, ny)
        if pursuer:
            score = -d * 1000 + wp * (-2)
            if close:
                # cut-off: move to reduce opponent escape by occupying cells aligned with opponent
                ax = 1 if ox > nx else (-1 if ox < nx else 0)
                ay = 1 if oy > ny else (-1 if oy < ny else 0)
                # prefer stepping in the direction that would keep opponent within a "strip"
                strip = (ax == 0) or (ay == 0)
                score += (200 if strip else 0)
            candidates.append((score, wp, d, nx, ny))
        else:
            score = d * 1000 - wp * 2
            if close:
                # flee to farthest corner from pursuer
                corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
                far_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
                dc = abs(nx - far_corner[0]) + abs(ny - far_corner[1])
                score += dc * 3
            candidates.append((score, -wp, -d, nx, ny))

    if not candidates:
        return [0, 0]
    candidates.sort(reverse=True)
    _, _, _, nx, ny = candidates[0]
    return [nx - sx, ny - sy]
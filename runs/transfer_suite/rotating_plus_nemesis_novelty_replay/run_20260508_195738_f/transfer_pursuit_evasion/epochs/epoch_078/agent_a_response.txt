def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role", "") or "").lower()
    opp_role = str(observation.get("opponent_role", "") or "").lower()
    self_is_pursuer = ("purs" in self_role) or ("purs" in opp_role and "evad" in self_role)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if self_is_pursuer:
        target_corner = max(corners, key=lambda c: md(c[0], c[1], ox, oy))
        def score(nx, ny):
            d_opp = md(nx, ny, ox, oy)
            d_corner = md(nx, ny, target_corner[0], target_corner[1])
            return (-d_opp * 1000) + (-d_corner) - (1 if (nx, ny) in obstacles else 0) * 100000
    else:
        target_corner = max(corners, key=lambda c: md(c[0], c[1], sx, sy))
        def score(nx, ny):
            d_opp = md(nx, ny, ox, oy)
            d_corner = md(nx, ny, target_corner[0], target_corner[1])
            return (d_opp * 1000) + (-d_corner) - (1 if (nx, ny) in obstacles else 0) * 100000

    best_s = -10**18
    best = (sx, sy)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                s = score(nx, ny)
                if s > best_s:
                    best_s = s
                    best = (nx, ny)

    dx = best[0] - sx
    dy = best[1] - sy
    if dx < -1: dx = -1
    if dx > 1: dx = 1
    if dy < -1: dy = -1
    if dy > 1: dy = 1
    return [int(dx), int(dy)]
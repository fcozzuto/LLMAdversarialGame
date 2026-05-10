def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_role = str(observation.get("self_role", "") or "").lower()
    opponent_role = str(observation.get("opponent_role", "") or "").lower()
    self_is_evader = ("evad" in self_role) or ("escape" in self_role) or ("purs" in opponent_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    sgn = lambda a: 0 if a == 0 else (1 if a > 0 else -1)
    pref_dx, pref_dy = sgn(ox - sx), sgn(oy - sy)

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = manh(nx, ny, ox, oy)
        if self_is_evader:
            # Prefer increasing distance; slight penalty for closeness to obstacles.
            near_obs = 0
            for ax, ay in obstacles:
                if abs(ax - nx) <= 1 and abs(ay - ny) <= 1:
                    near_obs += 1
            score = (d * 100) - near_obs * 3
        else:
            # Prefer decreasing distance.
            score = (-d * 100)
        # Deterministic tie-break: prefer toward preferred direction, then lexicographic.
        score2 = (score, -abs(dx - pref_dx) - abs(dy - pref_dy), -abs(dx) - abs(dy), dx, dy)
        if best is None or score2 > best[0]:
            best = (score2, (dx, dy))

    if best is None:
        return [0, 0]
    dx, dy = best[1]
    return [int(dx), int(dy)]
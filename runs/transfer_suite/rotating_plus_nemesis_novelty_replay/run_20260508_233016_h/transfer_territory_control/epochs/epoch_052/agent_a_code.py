def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    ox, oy = observation.get("opponent_position", (sx, sy))

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        obstacles.add(tuple(p))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: man(c[0], c[1], ox, oy))

    cand = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = None
    best_score = None

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Prefer approaching farthest corner while staying away from opponent
        score = (man(nx, ny, far_corner[0], far_corner[1]) * 1.0) - (man(nx, ny, ox, oy) * 1.5)
        # Prefer unvisited-ish cells if path info exists
        sp = set(map(tuple, observation.get("self_path") or []))
        if (nx, ny) in sp:
            score -= 0.25
        # Tie-break deterministically
        if best is None or score < best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        # Fallback: move toward a corner if possible, else toward away from opponent
        tx, ty = far_corner
        dx = -1 if sx > tx else (1 if sx < tx else 0)
        dy = -1 if sy > ty else (1 if sy < ty else 0)
        for ddx, ddy in ([dx, 0], [0, dy], [-1, 0], [1, 0], [0, -1], [0, 1], [0, 0]):
            nx, ny = sx + ddx, sy + ddy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [ddx, ddy]
        return [0, 0]
    return best
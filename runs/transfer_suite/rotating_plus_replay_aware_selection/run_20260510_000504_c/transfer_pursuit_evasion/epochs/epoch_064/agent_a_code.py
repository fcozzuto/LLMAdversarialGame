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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    tcx, tcy = max(corners, key=lambda c: manh(c[0], c[1], ox, oy))

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        d = manh(nx, ny, ox, oy)
        d_corner = manh(nx, ny, tcx, tcy)

        if self_is_evader:
            # Prefer increasing distance; if tied, prefer moving toward farthest corner.
            score = d * 100 - d_corner
            # Avoid accidental capture.
            if nx == ox and ny == oy:
                score -= 100000
        else:
            # Pursuer: prefer decreasing distance; if tied, move toward opponent's cell.
            score = -d * 100 - manh(nx, ny, ox, oy)
            # If already at opponent, capture likely; keep it.
            if nx == ox and ny == oy:
                score += 100000

        # Deterministic tie-break: lexicographic on (dx, dy)
        if best is None or score > best_score or (score == best_score and (dx, dy) < best):
            best = (dx, dy)
            best_score = score

    if best is None:
        return [0, 0]
    return [best[0], best[1]]
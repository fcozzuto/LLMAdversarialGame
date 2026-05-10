def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "")).lower()
    we_evader = ("evader" in role) or ("runner" in role)

    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def cell_pen(x, y):
        if x < 0 or x >= w or y < 0 or y >= h:
            return 10
        pen = 0
        if (x, y) in blocked:
            return 1000
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) in blocked:
                    pen += 1
        return pen

    # Small deterministic tiebreak preference: fewer steps away from staying (centered).
    def tiebreak(dx, dy):
        return abs(dx) + abs(dy)

    best_move = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        nd = dist(nx, ny, ox, oy)
        pen = cell_pen(nx, ny)

        if we_evader:
            # Prefer increasing distance; avoid obstacles; keep away from opponent's "next corridor"
            score = nd * 5 - pen * 3
            # Mild bias: if opponent is close to a corner, move along the opposite diagonal
            cx = 0 if ox < w - 1 - ox else w - 1
            cy = 0 if oy < h - 1 - oy else h - 1
            score += dist(nx, ny, cx, cy) * 0.3
        else:
            # Pursuer: minimize distance with stronger obstacle penalty
            score = -nd * 6 - pen * 5
            # Encourage cutting off toward opponent's approximate direction
            score += (-tiebreak(dx, dy)) * 0.1

        if best_score is None or score > best_score or (score == best_score and tiebreak(dx, dy) < tiebreak(best_move[0], best_move[1])):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
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

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_move = (0, 0)
    best_score = None

    if self_is_pursuer:
        # Pursuer: minimize distance to opponent; also prefer moving toward farthest corner to prevent getting trapped.
        target_corner = max(corners, key=lambda c: md(c[0], c[1], sx, sy))
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            d_opp = md(nx, ny, ox, oy)
            d_corner = md(nx, ny, target_corner[0], target_corner[1])
            # smaller is better; strong penalty for being further from opponent
            score = d_opp * 1000 + d_corner
            if best_score is None or score < best_score or (score == best_score and (dx, dy) < best_move):
                best_score = score
                best_move = (dx, dy)
    else:
        # Evader: maximize distance from opponent; bias toward the farthest corner.
        target_corner = max(corners, key=lambda c: md(c[0], c[1], ox, oy))
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            d_opp = md(nx, ny, ox, oy)
            d_corner = md(nx, ny, target_corner[0], target_corner[1])
            # larger is better
            score = d_opp * 1000 + d_corner
            if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
                best_score = score
                best_move = (dx, dy)

    dx, dy = best_move
    if (dx, dy) == (0, 0):
        return [0, 0]
    return [int(dx), int(dy)]
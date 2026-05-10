def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set()
    for p in observation.get("obstacles", []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((p[0], p[1]))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        d = abs(x1 - x2)
        e = abs(y1 - y2)
        return d if d > e else e
    def obstacle_prox(x, y):
        if not obstacles:
            return 0
        best = 10**9
        for bx, by in obstacles:
            dx = x - bx
            if dx < 0: dx = -dx
            dy = y - by
            if dy < 0: dy = -dy
            d = dx if dx > dy else dy
            if d < best: best = d
            if best == 0: break
        return best
    self_role = str(observation.get("self_role", "")).lower()
    is_pursuer = ("purs" in self_role) or ("police" in self_role)
    best_move = (0, 0)
    if is_pursuer:
        best_score = None
        # Prefer moves that minimize capture distance; tie-break with safer positioning.
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            dist = cheb(nx, ny, ox, oy)
            safe = obstacle_prox(nx, ny)
            score = (-dist, -safe, dx, dy)
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)
    else:
        best_score = None
        # Evader: maximize distance from pursuer; avoid obstacles by keeping safer cells.
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            dist = cheb(nx, ny, ox, oy)
            safe = obstacle_prox(nx, ny)
            score = (dist, safe, -dx, -dy)
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]
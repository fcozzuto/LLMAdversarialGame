def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not resources or not legal:
        return [0, 0]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    best = None
    for dx, dy, nx, ny in legal:
        # One-step lookahead: pick the resource where we gain the most over opponent.
        best_key_for_move = None
        best_val_for_move = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            self_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            # Primary: win likelihood margin (bigger is better). Secondary: closer self.
            val = (opp_d - self_d, -self_d)
            key = (val[0], val[1], rx, ry)
            if best_key_for_move is None or key > best_key_for_move:
                best_key_for_move = key
                best_val_for_move = val
        # Tie-break consistently by lexicographic (dx,dy).
        overall_key = (best_key_for_move[0], best_key_for_move[1], -dx, -dy)
        if best is None or overall_key > best[0]:
            best = (overall_key, (dx, dy))
    return [best[1][0], best[1][1]]
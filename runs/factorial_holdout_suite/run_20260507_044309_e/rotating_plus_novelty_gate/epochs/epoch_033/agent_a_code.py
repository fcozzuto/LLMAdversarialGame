def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def dist(x1, y1, x2, y2):
        dx = x1 - x2; dx = dx if dx >= 0 else -dx
        dy = y1 - y2; dy = dy if dy >= 0 else -dy
        return dx + dy
    resources = observation.get("resources", []) or []
    valid = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]
    if not resources:
        tx, ty = w // 2, h // 2
        best = None; best_d = 10**9; best_i = 10**9
        for i, (dx, dy, nx, ny) in enumerate(valid):
            d = dist(nx, ny, tx, ty)
            if d < best_d or (d == best_d and i < best_i):
                best = (dx, dy); best_d = d; best_i = i
        return [best[0], best[1]]
    resources2 = [(r[0], r[1]) for r in resources]
    best_move = None; best_score = -10**18
    for i, (dx, dy, nx, ny) in enumerate(valid):
        my_d = min(dist(nx, ny, rx, ry) for rx, ry in resources2)
        opp_d = min(dist(ox, oy, rx, ry) for rx, ry in resources2)
        score = (opp_d - my_d) * 1000 - my_d
        if score > best_score:
            best_score = score; best_move = (dx, dy)
        elif score == best_score and i < valid.index((best_move[0], best_move[1], sx + best_move[0], sy + best_move[1])):
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]
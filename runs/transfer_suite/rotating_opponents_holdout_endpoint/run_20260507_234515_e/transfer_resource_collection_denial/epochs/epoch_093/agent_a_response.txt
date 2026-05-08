def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        return [dx, dy]
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # Evaluate: win race to nearest contested resource + bias toward immediate pickups.
        min_s = 10**9
        min_o = 10**9
        on_res = False
        for rx, ry in resources:
            dsi = dist(nx, ny, rx, ry)
            doi = dist(ox, oy, rx, ry)
            if dsi < min_s: min_s = dsi
            if doi < min_o: min_o = doi
            if rx == nx and ry == ny:
                on_res = True
                break
        val = (0 if not on_res else 10000)
        # contest: prefer reducing our lead over opponent to closest resource
        val += (min_o - min_s) * 50
        # secondary: prefer closer to any resource
        val += -min_s
        # micro-avoid: don't step into obvious dead corner if possible
        edge_pen = 0
        if nx == 0 or nx == w - 1: edge_pen += 0.5
        if ny == 0 or ny == h - 1: edge_pen += 0.5
        val += -edge_pen
        if val > best_val or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = val
            best_move = [dx, dy]
    return best_move
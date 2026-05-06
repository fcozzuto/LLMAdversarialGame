def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation.get('self_position', (0, 0))
    ox, oy = observation.get('opponent_position', (0, 0))
    resources = observation.get('resources', []) or []
    obstacles = set(tuple(p) for p in (observation.get('obstacles', []) or []))
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18

    target_list = [tuple(r) for r in resources if tuple(r) not in obstacles]
    if not target_list:
        target_list = [(ox, oy)]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        val = 0
        # Pick a deterministic best target after moving: maximize score margin.
        for tx, ty in target_list:
            ds = cheb(nx, ny, tx, ty)
            do = cheb(ox, oy, tx, ty)
            # Prefer targets we can reach sooner; also slightly prefer nearer to target.
            margin = do - ds
            val = margin * 1000 - ds
            if val > best_val:
                best_val = val
                best_move = [dx, dy]
    return best_move
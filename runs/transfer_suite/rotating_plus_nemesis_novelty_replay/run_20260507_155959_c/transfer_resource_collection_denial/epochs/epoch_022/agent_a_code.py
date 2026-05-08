def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = {(p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2}
    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18
    # target: nearest resource; if none, just move to maximize distance from opponent
    if resources:
        tx, ty = min(((p[0], p[1]) for p in resources if isinstance(p, (list, tuple)) and len(p) >= 2),
                     key=lambda p: man(sx, sy, p[0], p[1]))
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            d_res = man(nx, ny, tx, ty)
            d_opp = man(nx, ny, ox, oy)
            # prefer closer to resource, farther from opponent; deterministic tie-break by (dx,dy)
            score = (-d_res * 1000) + (d_opp * 10) + (dx * 0.1) + (dy * 0.01)
            if score > best_score:
                best_score = score
                best_move = (dx, dy)
    else:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            d_opp = man(nx, ny, ox, oy)
            score = d_opp * 1000 + (dx * 0.1) + (dy * 0.01)
            if score > best_score:
                best_score = score
                best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]
def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy
    if not resources:
        # deterministic drift toward top-right while avoiding obstacles
        cx, cy = w - 1, 0
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obst:
                key = (man(nx, ny, cx, cy), dx, dy)
                if best is None or key < best[0]:
                    best = (key, [dx, dy])
        return best[1] if best else [0, 0]
    best_move = [0, 0]
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        # intercept: target where we are closer than opponent; if impossible, minimize our disadvantage
        best_for_move = None
        for rx, ry in resources:
            d_me = man(nx, ny, rx, ry)
            d_opp = man(ox, oy, rx, ry)
            # Primary: prefer becoming closer by margin; Secondary: prefer taking soon; Tertiary: avoid giving opponent advantage
            # Key lower is better.
            key = (d_me - d_opp, d_me, -(d_opp - d_me), rx, ry)
            if best_for_move is None or key < best_for_move:
                best_for_move = key
        if best_for_move is None:
            continue
        # Small tie-break to reduce oscillation: prefer not moving away from opponent
        opp_dist = man(nx, ny, ox, oy)
        final_key = (best_for_move[0], best_for_move[1], best_for_move[2], opp_dist, dx, dy)
        if best_key is None or final_key < best_key:
            best_key = final_key
            best_move = [dx, dy]
    return best_move if best_key is not None else [0, 0]
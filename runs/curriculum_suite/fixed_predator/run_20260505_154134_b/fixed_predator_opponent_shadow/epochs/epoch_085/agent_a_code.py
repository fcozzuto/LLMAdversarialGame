def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # If any resource is exactly blocked by an obstacle, still allow moving generally;
    # we just avoid stepping onto obstacles.
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_val = None

    # Deterministic resource order for tie-breaking
    resources_sorted = sorted((int(x), int(y)) for x, y in resources)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # Evaluate this move by aiming for the resource where we gain most advantage (opp closer than us).
        val = None
        for rx, ry in resources_sorted:
            our_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            # Higher is better: prioritize resources where opp is closer; also prefer smaller our_d to secure it.
            score = (opp_d - our_d) * 10 - our_d
            if val is None or score > val:
                val = score
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]
        elif val == best_val:
            # Stable tie-break: lexicographic by move order already deterministic, but enforce.
            if [dx, dy] < best_move:
                best_move = [dx, dy]

    return best_move if best_val is not None else [0, 0]
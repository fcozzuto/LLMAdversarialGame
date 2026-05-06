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

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # Choose the best resource from the hypothetical new position, then maximize advantage.
        local_best_key = None
        for rx, ry in resources:
            self_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            # Higher is better: who is closer after we move, then prefer closer-to-claim, then tie-break by resource position.
            key = (opp_d - self_d, -self_d, -rx, -ry, -cheb(ox, oy, rx, ry))
            if local_best_key is None or key > local_best_key:
                local_best_key = key

        if local_best_key is None:
            continue

        # Also include immediate proximity gain to discourage dithering.
        immediate = cheb(sx, sy, sx, sy)  # 0, just to keep deterministic structure
        total_score = (local_best_key[0], local_best_key[1], -abs((nx - sx)) - abs((ny - sy)), local_best_key[2], immediate)

        if best_score is None or total_score > best_score:
            best_score = total_score
            best_move = [dx, dy]

    return best_move
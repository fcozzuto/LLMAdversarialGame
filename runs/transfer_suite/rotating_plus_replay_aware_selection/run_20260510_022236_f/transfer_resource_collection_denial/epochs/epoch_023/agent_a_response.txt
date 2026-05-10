def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)

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

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            legal.append((dx, dy))

    if not legal:
        return [0, 0]

    # Deterministic target scoring: pick resources we can secure sooner (or deny if tied)
    best_key = None
    best_move = (0, 0)
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        best_target_score = -10**18
        best_target_dist = 10**9
        for rx, ry in resources:
            rx, ry = int(rx), int(ry)
            if not inb(rx, ry) or (rx, ry) in obs:
                continue
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Advantage first; then prefer closer targets; then prefer moves that reduce opponent progress
            adv = od - sd
            can_secure = 1 if sd < od else (0 if sd > od else -1)  # secure > tie > behind
            score = (can_secure * 10**6) + adv * 1000 - sd
            if score > best_target_score or (score == best_target_score and sd < best_target_dist):
                best_target_score = score
                best_target_dist = sd
        # Also add a small bias to keep moving toward the currently best target direction
        if best_key is None or (best_target_score, -best_target_dist) > best_key:
            best_key = (best_target_score, -best_target_dist)
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
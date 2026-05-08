def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    self_role = str(observation.get("self_role") or "").lower()
    opp_role = str(observation.get("opponent_role") or "").lower()
    we_evader = ("evader" in self_role) or ("pursuer" not in self_role and "evader" in opp_role)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Avoid immediately stepping into "contact lanes" near opponent (small deterministic penalty)
    def lane_pen(x, y):
        d = cheb(x, y, ox, oy)
        if d <= 1:
            return 1000
        # Penalize moves that align with opponent on row/col/diag (evader), helps against zigzag pursuer
        if x == ox or y == oy or abs(x - ox) == abs(y - oy):
            return 3
        return 0

    parity_target = (ox + oy) & 1

    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dist = cheb(nx, ny, ox, oy)
        pen = lane_pen(nx, ny)
        if we_evader:
            # maximize distance; tie-break by parity-change to disrupt zigzag pattern
            parity = (nx + ny) & 1
            parity_score = 0 if parity != parity_target else 1
            key = (dist, -parity_score, -(nx == ox and ny == oy), -pen)
            if best_key is None or key > best_key:
                best_key = key
                best_move = (dx, dy)
        else:
            # pursuer: minimize distance; tie-break by "cutting off" toward reducing opponent's options
            # (proxy: prefer moves that are closer in both x and y when possible)
            cut = (abs(nx - ox) - abs(sx - ox)) + (abs(ny - oy) - abs(sy - oy))
            key = (-dist, cut, -pen)
            if best_key is None or key > best_key:
                best_key = key
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
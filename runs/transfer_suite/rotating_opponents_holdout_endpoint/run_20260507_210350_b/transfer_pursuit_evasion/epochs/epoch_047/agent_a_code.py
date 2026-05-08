def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    rolestr = (observation.get("self_role", "") or "").lower()
    is_evader = any(k in rolestr for k in ("evader", "escape", "flee", "runner"))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    opp_edge_bias = 0
    if ox in (0, w - 1) or oy in (0, h - 1):
        opp_edge_bias = 1

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        return dx if dx > dy else dy

    def edge_dist(x, y):
        return min(x, w - 1 - x, y, h - 1 - y)

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        d = cheb(nx, ny, ox, oy)

        # Pursuer: greedy but also steer to edges/corners.
        if not is_evader:
            # Prefer reducing distance most; then reduce distance in the "dominant" axis; then push toward opponent edges.
            dom = (abs(ox - nx) >= abs(oy - ny))
            axis_term = abs((ox - nx) if dom else (oy - ny))
            corner_push = (edge_dist(ox, oy) * 0.6 + (0 if (ox in (0, w - 1) or oy in (0, h - 1)) else 1.0))
            # If opponent already on edge, more aggressively close.
            val = -d * 10.0 - axis_term * 0.8 - corner_push * 0.3 - opp_edge_bias * d * 0.2
        else:
            # Evader: maximize distance; prefer staying away from obstacles by lightly favoring moves with larger local edge distance.
            val = d * 10.0 + edge_dist(nx, ny) * 0.7

        if best_val is None:
            best_val = val
            best_move = (dx, dy)
        else:
            if val > best_val:
                best_val = val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
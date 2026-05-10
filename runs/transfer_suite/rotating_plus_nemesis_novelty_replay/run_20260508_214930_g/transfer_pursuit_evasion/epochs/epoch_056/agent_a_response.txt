def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for b in obstacles:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = observation.get("self_role") or "pursuer"
    pursuer = str(self_role).lower() == "pursuer"

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best_move = [0, 0]
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist = cheb(nx, ny, ox, oy)
        # pursuer: minimize distance; evader: maximize distance
        val = -dist if pursuer else dist

        # tie-break deterministically: prefer moves that keep distance strictly decreasing/increasing
        if best_val is None:
            best_val = val
            best_move = [dx, dy]
        else:
            if val > best_val:
                best_val = val
                best_move = [dx, dy]
            elif val == best_val:
                # secondary tie: prefer diagonal/forward toward intended objective by comparing sorted components
                if (abs(dx) + abs(dy), dx, dy) > (abs(best_move[0]) + abs(best_move[1]), best_move[0], best_move[1]):
                    best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]
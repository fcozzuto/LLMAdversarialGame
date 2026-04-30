def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = [tuple(r) for r in (observation.get("resources", []) or [])]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1,  0), (0,  0), (1,  0),
              (-1,  1), (0,  1), (1,  1)]

    # Build available moves (avoid obstacles and boundaries)
    moves = []
    for dx, dy in deltas:
        if dx == 0 and dy == 0:
            continue
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            moves.append((dx, dy))
    if not moves:
        return [0, 0]

    # Target closest resource if any
    target = None
    if resources:
        bestd = 10**9
        for rx, ry in resources:
            d = cheb(sx, sy, rx, ry)
            if d < bestd:
                bestd = d
                target = (rx, ry)

    # If no resources known, head toward opponent to pressure or block
    best_move = None
    best_score = -10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy

        # Basic scoring: prefer moving toward nearest resource if exists
        score = 0
        if target is not None:
            dist_to_target = cheb(nx, ny, target[0], target[1])
            score -= dist_to_target * 2  # emphasize closeness

        # Proximity to opponent: avoid stepping into immediate capture
        opp_dist = cheb(nx, ny, ox, oy)
        if opp_dist == 0:
            score -= 100  # would be on top; discourage
        else:
            score += max(0, 3 - opp_dist)

        # Encourage moving toward center region to deny space (simple heuristic)
        center_x, center_y = w // 2, h // 2
        score -= cheb(nx, ny, center_x, center_y)

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [best_move[0], best_move[1]]
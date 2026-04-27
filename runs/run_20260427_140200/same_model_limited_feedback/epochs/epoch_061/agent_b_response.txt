def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation.get('self_position', (0, 0))
    ox, oy = observation.get('opponent_position', (7, 7))
    resources = observation.get('resources', [])
    obstacles = observation.get('obstacles', [])
    obstacle_set = set((p[0], p[1]) for p in obstacles)

    def clamp_step(dx, dy, x, y):
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            return None
        if (nx, ny) in obstacle_set:
            return None
        return (nx, ny)

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def d2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    best = None
    best_val = None
    for rx, ry in resources:
        sd = d2(sx, sy, rx, ry)
        od = d2(ox, oy, rx, ry)
        # Prefer resources closer to self, but also deny ones much closer to opponent.
        val = (od - sd) * 2 - sd * 0.05
        # Small bias toward closer absolute progress.
        val += -0.001 * (rx + ry)
        if best is None or val > best_val:
            best = (rx, ry)
            best_val = val

    if best is None:
        return [0, 0]

    rx, ry = best
    # Choose the neighbor that minimizes distance to target; if ties, maximize distance from opponent.
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nxt = clamp_step(dx, dy, sx, sy)
        if nxt is None:
            continue
        nx, ny = nxt
        score = d2(nx, ny, rx, ry)
        opp_pen = -d2(nx, ny, ox, oy) * 0.001
        score = score + opp_pen
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            # deterministic tie-break: prefer moves with smaller |dx|+|dy|, then lexicographic
            if (abs(dx) + abs(dy), dx, dy) < (abs(best_move[0]) + abs(best_move[1]), best_move[0], best_move[1]):
                best_move = (dx, dy)

    # If best move unexpectedly invalid, ensure return is always allowed.
    nx = sx + best_move[0]
    ny = sy + best_move[1]
    if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacle_set:
        return [0, 0]
    return [best_move[0], best_move[1]]
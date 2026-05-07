def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)
    def step_towards(tx, ty):
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return dx, dy

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    moves = [(dx, dy) for dx, dy in dirs if dx != 0 or dy != 0] + [(0, 0)]

    def cell_free(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    # Choose best resource by comparing reachability vs opponent (materially different than pure nearest).
    best = None
    for rx, ry in resources:
        myd = dist(sx, sy, rx, ry)
        opd = dist(ox, oy, rx, ry)
        # Prefer resources we can reach sooner; tie-break closer to us, then deterministic coords.
        # Small bias to avoid chasing very far resources when competitive loss exists.
        score = (opd - myd, -myd, rx, ry)
        if best is None or score > best[0]:
            best = (score, (rx, ry))
    if best is not None:
        tx, ty = best[1]
        # One-step look with obstacle avoidance and keeping distance from opponent to prevent race losses.
        best_move = (None, None)  # (score, (dx,dy))
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not cell_free(nx, ny):
                continue
            my_next = dist(nx, ny, tx, ty)
            opp_next = dist(nx, ny, ox, oy)
            # Higher is better
            # - aggressively reduce distance to target
            # - if opponent is closer, prioritize moves that increase opponent distance
            # - slight preference for staying closer to target line
            race = dist(ox, oy, tx, ty) - my_next
            score = (race, -my_next, opp_next, dx, dy)
            if best_move[0] is None or score > best_move[0]:
                best_move = (score, (dx, dy))
        if best_move[1] is not None:
            return [int(best_move[1][0]), int(best_move[1][1])]

    # No visible resources: deterministically move toward the most "useful" corner (farthest from opponent)
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    cx, cy = max(corners, key=lambda p: (dist(p[0], p[1], ox, oy), -p[0], -p[1]))
    dx, dy = step_towards(cx, cy)
    nx, ny = sx + dx, sy + dy
    if cell_free(nx, ny):
        return [int(dx), int(dy)]

    # Fallback: choose safe move that maximizes distance from opponent.
    best_move = (None, (0, 0))
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not cell_free(nx, ny):
            continue
        score = (dist(nx, ny, ox, oy), -dist(nx, ny, cx, cy), dx, dy)
        if best_move[0] is None or score > best_move[0]:
            best_move = (score, (dx, dy))
    return [int(best_move[1][0]), int(best_move[1][1])]
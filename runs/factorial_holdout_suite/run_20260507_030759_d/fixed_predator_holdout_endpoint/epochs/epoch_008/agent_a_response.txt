def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles_raw)
    turns_remaining = observation.get("turns_remaining", 0)
    remaining_resource_count = observation.get("remaining_resource_count", len(resources))

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

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    valid_moves = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid_moves.append((dx, dy))
    if not valid_moves:
        return [0, 0]
    if not resources:
        tx, ty = w // 2, h // 2
        best = min(valid_moves, key=lambda d: cheb(sx + d[0], sy + d[1], tx, ty))
        return [best[0], best[1]]

    near_end = 1 if remaining_resource_count <= 4 or turns_remaining <= 6 else 0

    def best_target_for(nsx, nsy):
        best_val = None
        best_cell = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = cheb(nsx, nsy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            val = (od - sd) * 10 - sd
            if near_end:
                val = -sd * 3 + od
            if best_val is None or val > best_val or (val == best_val and (sd < cheb(ox, oy, rx, ry))):
                best_val = val
                best_cell = (rx, ry, sd, od)
        if best_cell is None:
            return (0, 0, 999, 999)
        return best_cell  # rx, ry, sd, od

    best_move = None
    best_score = None
    for dx, dy in valid_moves:
        nsx, nsy = sx + dx, sy + dy
        rx, ry, sd, od = best_target_for(nsx, nsy)
        score = (od - sd) * 10 - sd
        if near_end:
            score = -sd * 3 + od * 0.5
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
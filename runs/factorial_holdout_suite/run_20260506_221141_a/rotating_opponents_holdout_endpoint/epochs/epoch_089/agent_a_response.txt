def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def dist_cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Candidate moves: deterministic fixed order.
    cand = [(0, 0), (1, 1), (1, 0), (0, 1), (-1, 1), (1, -1), (-1, 0), (0, -1), (-1, -1)]
    best = (0, 0)
    best_val = -10**18

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        move_val = -10**18
        for rx, ry in resources:
            self_d = dist_cheb(nx, ny, rx, ry)
            opp_d = dist_cheb(ox, oy, rx, ry)

            lead = opp_d - self_d  # positive means we're closer (good)
            # Avoid chasing resources the opponent can grab at same/greater speed.
            if opp_d <= self_d:
                lead -= 6 + (self_d - opp_d)  # strong penalty to force material change
            # Prefer not just being closer, but becoming close quickly.
            urgency = -(self_d + 0.25 * (abs(rx - nx) + abs(ry - ny)))
            val = lead * 10 + urgency

            if val > move_val:
                move_val = val

        if move_val > best_val:
            best_val = move_val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]
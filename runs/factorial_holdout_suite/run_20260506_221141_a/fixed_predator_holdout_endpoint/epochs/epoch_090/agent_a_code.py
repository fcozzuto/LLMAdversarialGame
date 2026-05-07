def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        x, y = int(r[0]), int(r[1])
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))
    if not resources:
        return [0, 0]

    def dist_cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = (-1, 0, 1)
    best_move = [0, 0]
    best_val = None

    # One-step look: choose move that maximizes the best "deny/secure" value among remaining resources.
    for dx in moves:
        for dy in moves:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue

            best_here = None
            for rx, ry in resources:
                self_d = dist_cheb(nx, ny, rx, ry)
                opp_d = dist_cheb(ox, oy, rx, ry)
                val = opp_d - self_d
                if self_d == 0:
                    val = val + 1000  # immediate collection
                # Tie-break: prefer smaller self distance after maximizing denial.
                val = val * 1000 - self_d
                if best_here is None or val > best_here:
                    best_here = val

            if best_val is None or best_here > best_val:
                best_val = best_here
                best_move = [dx, dy]

    return best_move
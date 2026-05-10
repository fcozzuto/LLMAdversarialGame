def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for t in observation.get("obstacles") or []:
        if isinstance(t, (list, tuple)) and len(t) >= 2:
            x, y = int(t[0]), int(t[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    is_pursuer = ("pursu" in role) or ("hunter" in role) or ("seeker" in role)

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def free_neighbors(x, y):
        cnt = 0
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                cnt += 1
        return cnt

    def wall_bite(x, y):
        # Prefer staying away from blocked edges only when tied; corners are often bad for evader.
        edge = 0
        if x == 0 or x == w - 1: edge += 1
        if y == 0 or y == h - 1: edge += 1
        return edge

    best = None
    best_val = None
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        ddx, ddy = nx - ox, ny - oy
        dist2 = ddx * ddx + ddy * ddy

        openness = free_neighbors(nx, ny)
        avoid_wall = wall_bite(nx, ny)

        if is_pursuer:
            # Chase while staying in more open tiles (avoid getting funneled by obstacles).
            val = (-dist2) + (0.6 * openness) - (0.2 * avoid_wall)
        else:
            # Evade: maximize distance; also avoid corners and reduce being trapped.
            val = (dist2) + (0.3 * openness) - (0.8 * avoid_wall)

        # Tie-break deterministically: prefer closer-to-opponent projection for pursuer, else farther.
        if best is None or val > best_val or (val == best_val and ((dist2 < (best[0]-ox)*(best[0]-ox)+(best[1]-oy)*(best[1]-oy)) if is_pursuer else (dist2 > (best[0]-ox)*(best[0]-ox)+(best[1]-oy)*(best[1]-oy)))):
            best = (nx, ny)
            best_val = val

    if best is None:
        return [0, 0]
    dx, dy = best[0] - sx, best[1] - sy
    dx = -1 if dx < -1 else (1 if dx > 1 else dx)
    dy = -1 if dy < -1 else (1 if dy > 1 else dy)
    return [int(dx), int(dy)]
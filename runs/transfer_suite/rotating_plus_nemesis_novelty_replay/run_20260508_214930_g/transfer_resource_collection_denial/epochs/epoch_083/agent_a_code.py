def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick resource we can likely arrive at earlier than opponent.
    best_t = resources[0]
    best_s = -10**9
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer nearer to us; strongly prefer resources opponent is farther from.
        score = -ds + 0.35 * (do - ds)  # higher is better
        # Small deterministic bias to prevent ties.
        score += -0.001 * (rx + 7 * ry)
        if score > best_s:
            best_s = score
            best_t = (rx, ry)

    tx, ty = best_t

    moves = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,0), (0,1), (1,-1), (1,0), (1,1)]
    best_move = (0, 0)
    best_val = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        on_resource = 1 if (nx, ny) in set(resources) else 0
        ns = cheb(nx, ny, tx, ty)
        no = cheb(nx, ny, ox, oy)  # mild avoidance of moving into opponent reach
        # Tie-break: maximize capture, then minimize distance to target, then move away from opponent.
        val = 1000 * on_resource - 10 * ns + 0.03 * no - 0.001 * (abs(nx - tx) + abs(ny - ty))
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]